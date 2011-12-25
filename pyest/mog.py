# encoding: utf-8
"""


"""

from __future__ import division

__all__ = ['MOGEnsemble', 'AIMOGEnsemble']

import numpy as np

import mixtures
from ensemble import Ensemble

class MOGEnsemble(Ensemble):
    def __init__(self, *args, **kwargs):
        self.K = kwargs.pop('K', 10)
        super(MOGEnsemble, self).__init__(*args, **kwargs)

    def propose_position(self, ensemble):
        s = np.atleast_2d(ensemble.pos)
        Ns = len(s)
        c = np.atleast_2d(self.pos)

        self.mixture = mixtures.MixtureModel(self.K, c)
        self.mixture.run_kmeans(verbose=False)
        self.mixture.run_em(verbose=False, regularization=1e-10)

        q = self.mixture.sample(Ns)
        newlnprob = self.get_lnprob(q)

        newQ = self.mixture.lnprob(q)
        oldQ = self.mixture.lnprob(s)

        lnpdiff = oldQ - newQ + newlnprob - ensemble.lnprob
        accept = (lnpdiff > np.log(self._sampler._random.rand(len(lnpdiff))))

        return q, newlnprob, accept

class AIMOGEnsemble(MOGEnsemble):
    def propose_position(self, ensemble):
        s = np.atleast_2d(ensemble.pos)
        Ns = len(s)
        c = np.atleast_2d(self.pos)

        ginv = np.linalg.inv(np.cov(c, rowvar=0))

        self.mixture = mixtures.MixtureModel(self.K, c)
        self.mixture.run_kmeans(ginv=ginv, verbose=False)
        self.mixture.run_em(verbose=False, regularization=1e-10, maxiter=2)

        q = self.mixture.sample(Ns)
        newlnprob = self.get_lnprob(q)

        newQ = self.mixture.lnprob(q)
        oldQ = self.mixture.lnprob(s)

        lnpdiff = oldQ - newQ + newlnprob - ensemble.lnprob
        accept = (lnpdiff > np.log(self._sampler._random.rand(len(lnpdiff))))

        return q, newlnprob, accept
