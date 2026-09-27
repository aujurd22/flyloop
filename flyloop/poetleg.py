"""Learning leg: tiny FlyPoet k-WTA GPTs trained online on the sequence lane.

v2: two streams.
  A — hidden regime (v1 replication, unidentifiable task: the mixture optimum
      is the marginal predictor).
  B — regime marker token prefixed to the context (identifiability arm; the
      oracle with known regime reaches ~0.639 error, stream A stalls at
      ~0.75-0.88).
Reuse: imports GPT/KWTA straight from D:\\djr82\\flypoet\\train_v2.py.
Mechanics kept from the surviving FlyPoet claims: few updates x partitioned
parameters, k-WTA at the 0.25 sweet spot. CUDA by default, permanent CPU
fallback on any CUDA hiccup.
"""
import sys

from . import config as C

sys.path.insert(0, C.FLYPOET_REPO)

import torch  # noqa: E402

torch.set_num_threads(2)

from train_v2 import GPT  # noqa: E402  (FlyPoet repo module)


class PoetLeg:
    """One k-WTA GPT + its trainable partition. V_in = vocab seen by the model;
    predictions are read from the first PREDICT_V channels only."""

    def __init__(self, tag, V_in, seq_len, predict_v, log=print):
        self.tag = tag
        self.predict_v = predict_v
        self.log = log
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        kwta_opts = {"impl": "torch", "k_frac": C.SEQ_K_FRAC, "selector": "magnitude"}
        self.model = GPT(V_in, d=C.SEQ_D, layers=C.SEQ_LAYERS, heads=C.SEQ_HEADS,
                         ffn_h=C.SEQ_FFN, seq=seq_len,
                         kwta_opts=kwta_opts).to(self.device)
        # stream identity, not arm: FULL-A and EPI-A share init (paired arms),
        # A and B differ (different streams)
        g = torch.Generator().manual_seed(C.SEED + (1 if tag.endswith("A") else 2))
        self.masks = {}
        for name, p in self.model.named_parameters():
            m = torch.rand(p.shape, generator=g) < C.SEQ_TRAIN_FRAC
            if not m.any():
                m.view(-1)[0] = True
            self.masks[name] = m.to(self.device)
        self.opt = torch.optim.AdamW(self.model.parameters(), lr=C.SEQ_LR)
        self.updates = 0
        npar = sum(p.numel() for p in self.model.parameters())
        self.log(f"[poet{tag}] device={self.device} params={npar / 1e3:.0f}K "
                 f"V={V_in} k_frac={C.SEQ_K_FRAC} train_frac={C.SEQ_TRAIN_FRAC}")

    def predict(self, ctx):
        self.model.eval()
        try:
            with torch.no_grad():
                x = torch.tensor([ctx], device=self.device)
                logits, _ = self.model(x)
                return int(logits[0, -1, :self.predict_v].argmax()), None
        except RuntimeError as e:
            return 0, self._fallback(e)

    def train_step(self, tokens):
        self.model.train()
        x = torch.tensor([tokens[:-1]], device=self.device)
        y = torch.tensor([tokens[1:]], device=self.device)
        try:
            _, loss = self.model(x, y)
            self.opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            with torch.no_grad():
                for name, p in self.model.named_parameters():
                    if name in self.masks and p.grad is not None:
                        p.grad.mul_(self.masks[name])
            self.opt.step()
            self.updates += 1
            return float(loss), None
        except RuntimeError as e:
            return None, self._fallback(e)

    def _fallback(self, err):
        if self.device == "cuda":
            self.log(f"[poet{self.tag}] CUDA error ({str(err)[:100]}); CPU fallback")
            self.device = "cpu"
            self.model.to("cpu")
            self.masks = {n: m.to("cpu") for n, m in self.masks.items()}
            return "cuda_fallback"
        return f"error:{str(err)[:120]}"

    def save(self, path):
        torch.save({"model": self.model.state_dict(),
                    "opt": self.opt.state_dict(),
                    "updates": self.updates,
                    "device": self.device}, path)

    def load(self, path):
        blob = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(blob["model"])
        self.opt.load_state_dict(blob["opt"])
        self.updates = blob.get("updates", 0)
        if blob.get("device") == "cpu" and self.device != "cpu":
            self.device = "cpu"
            self.model.to("cpu")
            self.masks = {n: m.to("cpu") for n, m in self.masks.items()}
