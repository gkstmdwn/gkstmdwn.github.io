---
title: Probability and Statistics 01. Dicrete Probability Distributions
date: 2024-06-26 13:15:00 +0900
categories: [Mathematics, Probability and Statistics]
tags: [math, probability_and_statistics, english]     # TAG names should always be lowercase
toc: true
math: true
# image: /assets/img/posts/
---

## 확률과 통계를 시작하기에 앞서
영어로 공부를 했기에 영어로 작성하였습니다. 한국어 글은 추후에 작성하겠습니다.  
확률과 통계를 공부하기에 앞서, 먼저 고등학교 수학과정을 복습하기를 권장합니다.  
특히 미분적분학이 중요하게 쓰입니다.  
따로 제가 공부하다가 부가 설명이 필요한 것 같은 부분은 작성해두었습니다.

## 자료
자료는 밑의 링크에서 찾을 수 있습니다.  
[Grinstead and Snell's Introduction to Probability](https://open.umn.edu/opentextbooks/textbooks/21) 사이트에 들어가셔서 pdf를 클릭하면 pdf파일 교재를 구할 수 있습니다.  

## 1.2) Discrete Probability Distributions
Chapter 1.1 explains about how to experiment probability distributions.  It isn't that important so we'll skip it and study from chapter 1.2

### Random Variables and Sample Spaces
Experiment: real or hypothetical progress in which the possible outcomes can be identified

#### Definition 1.1
- Random Variable: Ourcome of the experiment(Usually using a Roman letter like $X$ or $Y$)
- Sample Space: Set of all possible outcomes($\Omega$)
- If the sample space is countable(either finite or infinite) then the R.V.(random variable) is called discrete
- Event: Subset of a sample space(can be empty)
- Outcome: Element of a sample space  

These Definitions are **very important** and will be confusing later on.  
Please take time now to study and memorize the definitions.

#### e.g.) Roling a die
Our experiment will be rolling a die.  
Random Variable $X$: Outcome of the experiment  
The sample space is $\Omega=\\{1, 2, 3, 4, 5, 6\\}$, which is finite and countable.  
Therefore, $X$ is Discrete.  
  
Let's now define an event $E=\\{2,4,6\\}$, which is the result of the roll being an even number.  
You can also say that $X$ is even.

### Distribution Functions
For each outcome of the sample space, we will assign a **non-negative** number using a function m.  
This function is called a "Distribution Function".  
The distribution function is a function that takes a result of a experiment as input, and returns the probability of the output happening.  

#### Definition 1.2
Let's say $X$ is a Random Variable with finitely many possible outcomes.  
Then the **Distribution function for $X$** is a real-valued function $m:\Omega$ -> $R$ which satisfies:
1. $m(w)\geq0,$ $\forall w\in\Omega$
2. $\sum_{w\in\Omega}^{}m(w) = 1$  
  
For any subset $E$ of $\Omega$, the Probability of $E$( $P(E)$ ) is given by  

$$P(E)=\sum_{w\in E}^{}m(w)$$  

Cor. $\forall w\in\Omega,$ $P(\\{w\\}) = m(w)$  
  
We'll see some examples to get these concepts in mind. Again, these are the fundamental concepts going through all of Probability and Statistics, so it is never too much to spend this much time on Definition 1.1 and 1.2.

#### e.g.) Tossing 2 coins
$\Omega = \\{HH, HT, TH, TT\\}$  
Assuming that all the outcomes are equally likely,  
$m(HH)=m(HT)=m(TH)=m(TT)=1/4$  
If $E$ is the event where at least one head is obtained,  
$E=\\{HH,HT,TH\\},$ $\; P(E)=\sum_{w\in E}^{}m(w)=3/4$

#### e.g.) Rolling a die
$\Omega=\\{1,2,3,4,5,6\\}$  
Assuming that all the outcomes are equally likely,
$m(1)=m(2)=...=m(6)=1/6$  
$E=\\{2,4,6\\},$ $\; P(E)=3/6=1/2$  
  
You will be understanding these concepts now hopefully.

#### e.g.) A, B, C game
A, B, and C are playing a game that
- A and B have the same chance to win
- C has only half the chance of A or B  
$\Omega=\\{A, B, C\\}$  
These two statements below holds.
- $m(A)=m(B)=2*m(C)$
- $m(A)+m(B)+m(C)=1,$ by ii) of Definition 1.2  
Therefore, $m(C)=1/5, m(A)=m(B)=2/5$  
$E=\\{A,C\\}$ meaning that A or C wins.  
$P(E) = m(A) + m(C) = 3/5$

### Properties

#### Set Theory
Before Therom 1.1, We need to remind ourselves about Set Theory. Let's say $A$ and $B$ are sets.
- $A \cup B=\\{ x \vert x\in A \text{ or } x \in B\\}$
- $A \cap B=\\{ x \vert x\in A \text{ and } x \in B\\}$
- $A-B(A\setminus B) = \\{x \vert x\in A \text{ and } x \notin B\\}$
- $A \subseteq B$: $A$ is a subset of $B$ ($\forall x in A, \; x \in B$)
- $\bar{A} \text{ (Complement of } A \text{) } = \\{x \vert x\notin A, \; x \in \Omega\\}$

#### Theorem 1.1
1. $P(E) \geq 0, \; \forall E \subseteq \Omega$
2. $P(\Omega) = 1$
3. If $E \subseteq F \subseteq \Omega, \; P(E) \geq P(F)$
4. If $A$ and $B$ are disjoint(meaning that $A\cap B = \varnothing$), $\; P(A\cup B)=P(A)+P(B)$
5. $P(\bar{A})=1-P(A), \; \forall A \subseteq \Omega$  

We'll prove these 5 statements indivisually.  

1. $P(E) \geq 0, \; \forall E \subseteq \Omega$  
> $P(E) = \sum_{w \in E}^{} m(W)$  
> since $\ m\ $ is a non-negative function, $P(E) \geq 0$  
2. $P(\Omega) = 1$  
> $P(\Omega )= \sum_{w \in \Omega}^{}m(W) = 1$, from ii) of Definition 1.2  
3. If $E \subseteq F \subseteq \Omega, \; P(E) \geq P(F)$  
> Suppose that $E \subseteq F \subseteq \Omega$  
> $P(F)=\sum_{w\in F}^{}m(W)=\sum_{w\in E}^{}m(W)+\sum_{w\in F\cap E}^{}m(w)$  
> Since $m$ is a non-negative function, $\sum_{w\in E}^{}m(W)$ and $\sum_{w\in F\cap E}^{}m(w)$ are greater than $0$.  
> Therefore, $\sum_{w\in E}^{}m(W)+\sum_{w\in F\cap E}^{}m(w) \geq \sum_{w\in E}^{}m(W) = P(E)$  
4. If $A$ and $B$ are disjoint(meaning that $A\cap B = \varnothing$), $\; P(A\cup B)=P(A)+P(B)$  
> $P(A\cup B)=\sum_{w\in A\cup B}^{}m(w)=\sum_{w\in A}^{}m(w)+\sum_{w\in B}^{}m(w)+\sum_{w\in A\cap B}^{}m(w)$  
> Since $A$ and $B$ are disjoint, $A \cap B = \varnothing,\; \sum_{w\in A\cap B}^{}m(w) = 0$  
> So, $\sum_{w\in A\cup B}^{}m(w)=\sum_{w\in A}^{}m(w)+\sum_{w\in B}^{}m(w)=P(A)+P(B)$  
5. $P(\bar{A})=1-P(A), \; \forall A \subseteq \Omega$  
> $\Omega=A\cup \bar{A}$ since $A$ and $\bar{A}$ are disjoint.  
> $P(\Omega)=P(A)+P(\bar{A})$  
> $\therefore P(\bar{A})=1-P(A)$  

#### Theorem 1.2
$A_1 , \ A_2, \ ... \ , \ A_n$: pairwise disjoint subsets of $\Omega$  
> pairwise disjoint means that $\forall A_{i, \ j} , \; A_i \cap A_j=\varnothing$  
{: .prompt-tip }
  
$$P(\cup_{i=1}^{n}A_i)=\sum_{i=1}^{n}P(A_i)$$

#### Theorem 1.3
$A_1 , \ A_2, \ ... \ , \ A_n$: partition of $\Omega$  
> partition means that $\cup_{i=1}^{n}A_i=\Omega, \;\text{and} \; A_1 , \ A_2, \ ... \ , \ A_n \$are pairwise disjoint
{: .prompt-tip }

$$P(E)=\sum_{i=1}^nP(E\cap A_i)$$  
$E\cap A_1, \ ...\ , \ E\cap A_n$ is a partition of $E$  

proof) To prove that $E\cap A_1, \ ...\ , \ E\cap A_n$ is a partition of $E$, we must establish two properties
1. The sets $E\cap A_i$ are pairwise disjoint.  
2. The union of these sets equal $E$.  
Assume $\(A_1, \ldots, A_n\)$ form a partition of the sample space $\(\Omega\)$, which implies:
- $\(A_i \cap A_j = \varnothing\)$ for all $\(i \neq j\)$,
- $\(\bigcup_{i=1}^n A_i = \Omega\)$.

We aim to show that $\(E \cap A_1, \ldots, E \cap A_n\)$ form a partition of $\(E\)$. This requires demonstrating:
1. **Pairwise Disjoint**: $\((E \cap A_i) \cap (E \cap A_j) = \varnothing\)$ for all $\(i \neq j\)$,
2. **Complete Coverage**: $\(\bigcup_{i=1}^n (E \cap A_i) = E\)$.

##### Step 1: Pairwise Disjoint
To show $\((E \cap A_i) \cap (E \cap A_j) = \varnothing\)$ for $\(i \neq j\)$:
$$
\begin{align*}
\text{Suppose } x \in (E \cap A_i) \cap (E \cap A_j). \text{ Then:}\\
& x \in E \cap A_i \Rightarrow x \in E \text{ and } x \in A_i,\\
& x \in E \cap A_j \Rightarrow x \in E \text{ and } x \in A_j.\\
\text{Since } A_i \cap A_j = \varnothing, \text{ no } x \text{ can be in both } A_i \text{ and } A_j.\\
\Rightarrow (E \cap A_i) \cap (E \cap A_j) = \varnothing.
\end{align*}
$$

##### Step 2: Complete Coverage
To show $\(\bigcup_{i=1}^n (E \cap A_i) = E\)$:
$$
\begin{align*}
\text{"}\subseteq\text{": } & \text{If } x \in \bigcup_{i=1}^n (E \cap A_i), \text{ then } x \in E \cap A_i \text{ for some } i \Rightarrow x \in E.\\
\text{"}\supseteq\text{": } & \text{If } x \in E, \text{ since } \bigcup_{i=1}^n A_i = \Omega, \text{ and } x \in \Omega, \text{ there exists some } i \text{ such that } x \in A_i.\\
& \text{Therefore, } x \in E \cap A_i \text{ for some } i, \text{ and thus } x \in \bigcup_{i=1}^n (E \cap A_i).
\end{align*}
$$

#### Corollary 1.1
For any two events A and B,  

$$P(A)=P(A\cap B)+ P(A\cap \bar{B})$$

#### Theorem 1.4

$$P(A\cup B)=P(A)+P(B)-P(A\cap B)$$


### Uniform Distribution

#### Definition 1.3
If a sample space $\Omega$ has n elements, and $\Omega$ is uniformly distributed, the distribution function $m$ is defined by  

$$m(w) = \frac{1}{n}, \; \forall w \in \Omega$$

#### e.g.) Rolling 2 dice

$$\Omega=\{(i,\ j) \vert 1 \leq i,\ j \leq 6\}$$  

$$\vert \Omega \vert = 36$$  

if the outcome is uniformly distributed,  

$$\forall i,\ j,\; m((i,j))=\frac{1}{36}$$

### Infinite Sample Space
If sample space is countably infinite, meaning that there exists a bijection between sample space and $Z$(set of all integers), then the sample space is discrete.
> bijection means one-to-one corresponding.  
{: .prompt-tip }

#### e.g.) coin toss
If random variable $X$ is defined as the first time that a head is obtained.  
$\Omega = \\{1,2,3,...\\}$    
$\Omega$ has a bijection with $Z$, therefore $X$ is a discrete random variable.  

and if we continue with the example to calculate an event E where X is even:  
if $E = \\{2,4,6,...\\}$,  
$$P(E)=\sum_{w \in E}^{}m(w) = \frac{1}{4} + \frac{1}{16}+...=\frac{\frac{1}{4}}{1-\frac{1}{4}}=\frac {1}{3}$$