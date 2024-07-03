---
title: Probability and Statistics 02. Continuous Probability Densities
date: 2024-06-28 17:00:00 +0900
categories: [Mathematics, Probability and Statistics]
tags: [math, probability_and_statistics, english]     # TAG names should always be lowercase
toc: true
math: true
# image: /assets/img/posts/
---

## 2.2) Continuous Density Functions
Same as chapter 01, chapter 2.1 is about simulating, so we will skip it.  
  
We will start off by checking an example.  

### Density Functions of Continuous Random Variables

#### e.g.) Picking a Number
Let's pick a real number from the interval $[0,\ 1]$.  
In this case, we cannot define the distribution function as in Chapter 1.  
  
$\Omega=\\{r\vert r \in [0,1]\\}$
1. $P(0\leq X\leq 1) = 1$
2. $P(0\leq X\lt \frac{1}{2}) = \frac{1}{2}$  

These are true if you think intuitively.  
We want to define a function simillar to the distribution function in Chapter 1, using integrals.  
We will define $f(x)$ so that $\int_{E}^{}f(x)dx=P(E)$  
  
#### Sample Space
If sample space $\Omega \subseteq \mathbb{R}^n$ is uncountable, $X$ is a continuous random variable.  
> uncountable means that sample space is infinite, and sample space does not have a one to one bijection onto set of integers.
{: .prompt-tip }


#### Definition 2.1
If $X$ is a continuous random variable,
A "**Density Function**" of X is a real-valued function $f:\mathbb{R}^n \to \mathbb{R}$ so that
for any $a, b \in \mathbb{R}^1,$  
$P(a\leq X \leq b)=\int_{a}^{b}f(x)dx, \; P(X\in E)=\int_{E}f(x)dE$

To add a little more explanation on Def 2.1, density function $f(x)$ is like the distribution function for discrete random variable, but has some differences. 
For discrete random variables, the function took an input(e.g. 1) and returned the probability for that input. If I roll a die, $m(1) = \frac{1}{6}$. 
But for density functions, you cannot have a specific value as an input(think about the example of picking a number between 0 and 1). 
Therefore, we define the function so that the probability of 
an event happening can be derived from integrating the density function over the area of the event. Look at the example below. 

#### e.g.) continue from picking a number
Let's say that the density function of $X$ is $f(X)$.  

$$f(x) = \begin{cases} 
1 & \text{if } 0 < x < 1 \\
0 & \text{otherwise}
\end{cases}
$$  
  
Q. $E = \\{x\vert 0 \leq x \leq \frac{1}{2}\\}$  
$P(E)=\int_{E}f(x)dx=\int_{0}^{\frac{1}{2}}1dx=x\vert_{0}^{\frac{1}{2}}$
  
Q. What if we try to get the value of $P(X = 0)$?  
$P(E)=\int_{E}f(x)dx=\int_{0}^{0}f(x)dx=0$.  
You cannot calculate the probability of the output being a specific number for density functions. 
Might make more sense if you think that this is discrete and the sample space size is infinite. $1/\infty=0$.

### Cumulative Distribution Functions of Continuous Random Variables
We have seen that density functions are useful when considering continuous random variables. There is another kind of function, closely related to these density
functions, which is also of great importance. These functions are called **cumulative distribution functions**.

#### Definition 2.2
Let $X$ be a continuous r.v.  
Then, the cumulative distribution function of X is defined by the equation

$$ F_X(x) = P(X \leq x)$$

#### Theorm 2.1

$$F_X(x)=\int_{-\infty}^xf(t)dt$$  

$$\frac{d}{dx}F_X(x)=f(x)$$  

pf). By definition, 

$$ F_X(x) = P(X \leq x).$$

Let $E = (-\infty,x]$, Then

$$P(X\leq x)=P(X\in E),$$

which is

$$\int_{-\infty}^{x}f(t)dt.$$

#### e.g.)
Let's pick a real number chosen random from $[0,1]$, equally likely. Random Variable $X$ is square of the result.  
Q. What is density function of $X$?  
Let us define random variable $U$ be the chosen real number.
density function of $U$ is $g(t)$

$$g(t) = \begin{cases} 
1 & \text{if } 0 < t < 1 \\
0 & \text{otherwise}
\end{cases}
$$  

$$X = U^2$$

then for $0\leq x\leq 1$, cumulative distribution function $F_X$ of $X$ is

$$F_X(x)=P(X\leq x) = P(U^2\leq x) = P(U\leq \sqrt{x})=\int_{-\infty}^{\sqrt{x}}g(t)dt=\int_{0}^{\sqrt{x}}1dt=\sqrt{x}$$

$$F_X(x)= \begin{cases}
0 & x\lt 0 \\
\sqrt{x} & 0\leq x \leq 1 \\
1 & 1 \lt x
\end{cases}
$$

since density function can be get from differentiating cumulative distribution function,

$$f(x)=\begin{cases}
0 & x \lt 0 \\
\frac{1}{2}x^{-\frac{1}{2}} & 0\leq x \leq 1 \\
0 & 1 \lt x
\end{cases}
$$