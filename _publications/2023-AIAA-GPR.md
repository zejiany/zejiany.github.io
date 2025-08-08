---
title: "Pressure reconstruction from the measured pressure gradient using Gaussian process regression"
collection: publications
category: manuscripts
permalink: /publication/2023_AIAA_GPR
excerpt: 'This paper is about applying the Gaussian Process Regression (GPR) method to reconstruct the pressure fields from noisy pressure gradient observation. To evaluate the performance of proposed algorithm, a comparison is conducted between the GPR method and Omni-Directional Integration (ODI) method.'
year: 2023
venue: 'AIAA Scitech Conference Paper'
paperurl: 'https://arc.aiaa.org/doi/abs/10.2514/6.2023-0414'
bibtexurl: 'https://zejiany.github.io/files/you2023pressure.bib'
citation: 'You, Z., Wang, Q., & Liu, X. (2023). &quot;Pressure reconstruction from the measured pressure gradient using Gaussian process regression. &quot; <i>In AIAA SCITECH 2023 Forum </i>(p. 0414).'
---
Many numerical algorithms have been established to reconstruct pressure fields from measured kinematic data with noise by Particle Image Velocimetry (PIV), such as the Pressure Poisson solver and the Omni-Directional Integration (ODI) method. This study adopts Gaussian Process Regression (GPR), a probabilistic framework with an intrinsic de-noising mechanism to tackle drawbacks of traditional Pressure Poisson solver and compares the performance with ODI. To evaluate the accuracy of the algorithm, GPR and ODI are tested in detail in a canonical setup of forced homogeneous isotropic turbulence from the Johns Hopkins Turbulence Database. According to the result, GPR has the same level of accuracy as ODI with optimized hyper-parameters for the isotropic turbulence flow. However, GPR has the tendency to flatten impulsive signals. Therefore, without further modifications, it is not suitable to detect flow structures with impulsive true signals. The error propagation of the proposed framework is also analyzed and discussed in both physical and spectral spaces.