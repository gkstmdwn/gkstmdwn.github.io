---
title: Probability and Statistics 02. Continuous Probability Densities
date: 2024-06-28 17:00:00 +0900
categories: [Mathematics, Probability and Statistics]
tags: [math, probability_and_statistics, english]     # TAG names should always be lowercase
toc: true
math: true
# image: /assets/img/posts/
---

## 2.2 Continuous Density Functions
Same as chapter 01, chapter 2.1 is about simulating, so we will skip it.  
  
We will start off by checking an example.  

### e.g.) Picking a Number
Let's pick a real number from the interval $[0,\ 1]$.  
In this case, we cannot define the distribution function as in Chapter 1.  
  
$\Omega=\\{r\vert r \in [0,1]\\}$
1. $P(0\leq X\leq 1) = 1$
2. $P(0\leq X\lt \frac{1}{2}) = \frac{1}{2}$  

These are true if you think intuitively.  
We want to define a function simillar to the distribution function in Chapter 1, using integrals.  
We will define $f(x)$ so that $\int_{E}^{}f(x)dx=P(E)$  
  
### Sample Space
If sample space $\Omega \subseteq \mathbb{R}^n$ is uncountable, $X$ is a continuous random variable.  
> uncountable means that sample space is infinite, and sample space does not have a one to one bijection onto set of integers.
{: .prompt-tip }


### Definition 2.1
If $X$ is a continuous random variable,
A "**Density Function**" of X is a real-valued function $f:\mathbb{R}^n \to \mathbb{R}$ so that
for any $a, b \in \mathbb{R}^1,$
$P(a\leq X \leq b)=\int_{a}^{b}f(x)dx, \; P(X\in E)=\int_{E}f(x)dE$

### e.g.) continue from picking a number
Let's say that the density function of $X$ is $f(X)$.  

$$f(x) = \begin{cases} 
1 & \text{if } 0 < x < 1 \\
0 & \text{otherwise}
\end{cases}
$$  

Q. $E = \\{x\vert 0 \leq x \leq \frac{1}{2}\\}$  
$P(E)=\int_{E}f(x)dx=\int_{0}^{\frac{1}{2}}1dx=x\vert_{0}^{\frac{1}{2}}$