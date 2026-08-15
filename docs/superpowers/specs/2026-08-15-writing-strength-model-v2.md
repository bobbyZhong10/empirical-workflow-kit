# 措辞强度模型 v2 —— 经 14 篇 IS 顶刊语料校准

语料：14 篇（MISQ / MS / ISR，2012–2026），覆盖 DID、交错 DID、RDD、RDiT、IV/2SLS、
生存模型、结构估计、随机实验。抽取 278 条断言句、约 110 处降档实例。

---

## 一、原设计错在哪

我先验地设了单轴五档（T0 无限定因果 → T4 纯描述）。语料显示它在**核心区间**
（简约式因果句 + 观测数据）工作良好，但在四个方向系统性失效：

| 失效方向 | 语料证据 |
|---|---|
| **否定式/排除性断言** | "does not come at the expense of"、"cannot be explained by"、"we rule out"。举证结构是反的——依赖**功效**而非识别。同一句话在 n=10 万的设计和 n=57 的实验里含义完全不同，档位却相同。语料里 12 处 |
| **方法论断言** | "Estimating a static demand model would give biased elasticities"。语法上是标准 T0，但真值由推导而非数据决定，无经验承诺可证伪。结构论文把最无保留的因果语言用在**否定别人的方法**上，对自己的结论一律降到 T3 |
| **判别性论证** | "It is difficult to envision a selection process that would…"、"if this were the case, any observed effects would not be limited to…"。说服力来自**模式的选择性**，不来自动词。按字面判是 T3/T4，但它们承担全文最重的识别工作——**档位与论证权重恰好反向** |
| **模型内断言** | 模拟输出与有标准误的估计语法同构。"the total net gain would be 164.29 million dollars" 与 "reduces the probability by 21.60%" 在五档里无法区分 |

还有三处执行层面的崩塌：

- **"同句"规则由标点决定档位。**同一实质承诺写成两句是 T0，写成一句是 T1。语料里限定的
  实际作用域有四级：同句 / 段落级（"our findings are conditional on them"，覆盖此后全部结论）/
  章节级（"Even though the counterfactuals are 'partial'"，覆盖三个实验）/ 跨节前指（"we assess
  this in Appendix A"）。
- **T2 是三个现象的合并同类项**：同一主张的稳健性失败、平行构念上的零结果、假设方向被反转。
  第二类根本不是反证。因此"T2 密度"不可用于跨篇比较。
- **假设陈述（Hypothesis）语法上是 T0**。照单打档会把"提出待检验命题"记成"作无限定因果断言"。

---

## 二、修正后的模型

### 2.1 先分类型，再打档

档位只对 `world` 类型有意义。其余类型走各自的规则。

| 断言类型 | 判别 | 治理方式 |
|---|---|---|
| `world` | 关于研究对象的因果或关联断言 | 打 T0–T4 |
| `negative` | 排除性/否定式断言 | **不打档**。必须携带 `power_basis`：支撑该排除的检验、其样本量与最小可检测效应。缺 `power_basis` 一律降为 T3 措辞（"does not appear to be the primary driver"），禁止 "we rule out" |
| `methodological` | 断言对象是估计量或方法而非世界 | 不打档，但必须标类型，避免被计入实证强度统计 |
| `discriminating` | 论证形式为"若替代解释成立则应观察到 X" | 不打档，但**必须登记它排除的具体替代解释**。这类句子的低档位是正常的，检查器不得据此判定"证据弱" |
| `model_internal` | 无抽样不确定性的模型输出 | 必须携带 `as-modeled` 标记（语料里 `as we model` / `Given the model structure` 是最干净的分界词）。禁止使用 "significant" |
| `hypothesis` | 待检验命题 | 不打档 |

### 2.2 档位（仅 `world`），去掉"同句"约束

T0 无限定 / T1 有范围限定 / T2 因果断言 + 披露反证 / T3 关联或一致性 / T4 描述。

"同句"改为独立字段：

```
qualifier_scope: sentence | paragraph | section | cross_reference
```

`section` 与 `cross_reference` 级别的限定**允许**，但要求：限定语句本身必须被登记为一个
`scope_declaration`，且其覆盖范围显式声明。这样 P13 那种"一句 'partial' 覆盖三个实验、
但摘要里消失"的情形可被检出。

### 2.3 三个新维度——它们才是判别诚实与回避的变量

**（1）`counterevidence_prominence`：反证的显著度**

语料里同一份反证可以出现在五个位置，档位相同、实际约束力差一个数量级：

| 位置 | 例 |
|---|---|
| 括号内 | "attenuates the negative effects of language and cultural **(but not time zone)** differences" |
| 句尾并列，无转折词 | "a positive and significant impact on Reservations, **albeit with a relatively small coefficient, and no significant effect on Booked Days**" |
| 独立转折句 | "**However**, the coefficient of weitaonum is insignificant." |
| 脚注/尾注 | "it is **nearly impossible** to tease out the informational effect and reward effect separately."（全篇最重的机制局限） |
| 附录 | "**although the pre-treatment trends are not strictly parallel**…"（核心识别假设的部分失败，正文完全未提） |

**统计事实：14 篇中 8 篇，其单条最具威胁性的披露位于脚注、尾注或附录，而非正文。**

因此 T2 的"相邻披露"必须细化为可查的显著度等级，且规定：**当反证针对的是识别假设本身时，
prominence 必须达到"独立转折句 + 正文"级别**。

**（2）`underlying_precision`：该句依赖的估计的精度**

语料里最尖锐的三例：不显著的系数被赋予实质解释（"insignificantly different from zero and
slightly positive … implying that…"）；p<0.10 的系数在摘要里升为无标记因果动词（正文
"suggesting that…（10% 显著）" → 摘要 "generate"）；t=1.8 的横截面差异在摘要里写成既定事实。

这三句的**档位都很克制**，读起来毫无问题。五档量的是语法承诺，不是措辞与证据的匹配度。

**（3）由前两者导出的真正指标：残差**

```
overclaim_residual = 措辞档位强度 − 证据强度
```

其中证据强度由 claim 登记表已有的字段算出（assessment、是否收缩过、gate 状态、
支撑卡片 provenance）再叠加 `underlying_precision`。

- 残差为正 → **过度声称**，阻断
- 残差为负 → **浪费证据**，报告
- 这正是我原设计里"过强阻断、过弱报告"的正确形式化

---

## 三、降档动作库（12 类）与"诚实 vs 回避"的四条判据

判据（逐条可机器化）：

- **(a) 可定位性**：收缩是否绑定到具体规格/列号/变量/子样本
- **(b) 传导性**：收缩是否改变了下游文本（摘要/结论/标题）的措辞。**不传导 = 回避**
- **(c) 方向性**：是否说明偏误方向或后果，还是仅"应谨慎解读"
- **(d) 即时回收**：让步后是否在同句或下一句被 `However / Nevertheless / Overall / Encouragingly` 抵消

| # | 动作 | 触发 | 落点 | 判定 |
|---|---|---|---|---|
| 1 | **范围收缩** | 子样本失败 | T1 | 看传导。"our earlier reported effects **are driven by IT-using industries**"——摘要不带此限定 = 回避 |
| 2 | **机制降级为解释** | 机制不可识别 | T3 | **诚实**。14 篇中 13 篇都有。标记词：`We interpret … as reflecting` / `as a plausible explanation` / `We propose some potential mechanisms` |
| 3 | **零结果重述为排除性证据** | 机制/平衡检验为零 | T2/T3 | 分裂。判据是**是否承认"证据缺失 ≠ 缺失的证据"**：诚实者紧接着写 "an absence of evidence does not constitute evidence…" |
| 4 | **失败重述为方法缺陷** | 稳健性失败 | T2，主张不降 | **回避**。"not significant, **perhaps because of the limited power** … However, the direction and magnitude are consistent with our expectations." 只给一半解释 |
| 5 | **前置声明式收缩** | 设计上无法回答 | 主张撤回 | **最诚实**。"we are not taking a strong position that…"、"we are unable to draw meaningful inferences about…"。全篇因此没有一句 T0 |
| 6 | **偏误方向声明** | 测量误差/SUTVA | T1/T3 | 看方向对谁有利。声明的偏误方向若恰好使自己结论被高估且不回补 = 诚实；包装成"我们低估了"再接"因此真实效应更大" = 回避 |
| 7 | **让步—回收** | 平衡检验部分失败 | 净 T4，主张不降 | **回避**。模板：`Although [不利事实], [量级/引文]` + 下一句 `However/Overall/Encouragingly` 复位。**14 篇全部有此模板** |
| 8 | **位移与埋藏** | 不利事实与主张冲突 | 正文档位不变 | **回避**。8/14 篇的最重威胁性披露在脚注/附录 |
| 9 | **条件式安抚** | 无法检验的假设 | 表面 T3，无实质收缩 | **回避**。"**If** the share of gift purchases is small, the potential bias should be negligible."——条件本身从不被检验 |
| 10 | **研究议程化** | 任何限制 | 不降档 | **回避**。局限段 5 条中 3–4 条属此类是常态 |
| 11 | **对象替换** | 目标构念不可测 | T1 | **诚实**。"**rather than examining** the implications for SAP behavior, **we instead examine** their implications for ISV partnership decisions."——限制被兑换成一个能被数据支持的、较小的主张。全语料最干净的一类 |
| 12 | **自陈不可检验** | 机制设计上不可分 | 主张撤回/T3 | **最诚实**。"we **admittedly have no way of testing** this conjecture."——承认后不给补救 |

---

## 四、改变写作建议（不只是检查器）的四个统计事实

**1. 摘要强于正文是行业惯例，不是个别失误。**
45 组可比配对中：摘要更强 **30**、相同 9、更弱 4、保护性省略 2。**13/14 篇**至少有一处。

含义：规则不能写成"禁止摘要强于正文"，那会被全体违反从而失效。正确的规则是
**升档必须留痕**——摘要档位高于结果节时，记录升了几档、靠什么支撑。
四种升档手法（按频次）：删除同段反证 / 抹去基线或量级 / 换掉自我标注
（正文 "back-of-the-envelope estimation" → 摘要 "Our further analysis indicates"）/ 换动词。

**2. 强度峰值不总在摘要。**三种模式各有实例：引言 > 摘要；结论 > 摘要 > 结果（同一主张
T3 → T1 → T0 单调升级）；**标题 > 摘要 > 正文**（标题 "Optimizing"，正文明写
"we do not attempt to manipulate the policies to achieve optimality"）。
所以一致性检查必须覆盖标题。

**3. 局限性段落不是降档发生的地方。**降档发生在结果节内部（与失败同句或紧邻）和方法节。
两套话语互不引用——最脆弱的证据只在它首次出现的位置存在一次。
9 篇有独立局限小节的论文中，**3 篇的局限段完全不提正文已披露的任何失败**。

**4. 最反直觉、也最有用的一条：取消独立局限性小节，反而更诚实。**

清点 59 条局限性表述：真实约束 36、礼节性免责 16、半真实 6、执行失败 1。

- 有独立局限小节 = 9 篇，礼节性免责集中在其中三篇（5 条中 4 条 / 5 条中 3 条 / 5 条中 2 条）
- **无独立局限小节 = 5 篇，其中 4 篇的局限性表述全部为真实约束**

机制很清楚：**没有专门放局限的地方，局限就只能绑在它所影响的那条主张旁边**，于是必然带
列号、变量名、子样本，也就必然满足判据 (a)。极端案例是七条限制分别落在导言、§3、§4.4、
§4.4.3、§5.1.1（两条）、§5.2，每条都绑到具体列号，且至少两条承认失败后不给补救。

代价是读者要自己把散落的限制拼起来。

---

## 五、结构估计论文的特殊措辞（单列）

**identified vs calibrated 的语法分工极干净**：
- identified 一律被动或 "only … can be identified"：`the discount factor is usually not identified, so I do not attempt to estimate it`
- calibrated 一律第一人称主动设定 + 惯例背书：`I set all discount rates to be 0.996, which has been typically assumed for monthly data`；表格直接标 `0 (fixed)` / `1 (fixed)`

**一类五档看不见的实质降档：identified → simulated。**
"the magnitude of indirect effects … **is difficult to identify separately by the estimated parameters** …
**we apply simulations to explicitly quantify** the indirect effects"——该量从"有标准误的参数"
变为"无标准误的模拟输出"，语法上与其他效应量无法区分。

**反事实限定的三种做法**：一次性总括 + 自嘲引号（`Even though the counterfactuals are "partial,"`，
但该限定在摘要与结论中完全消失，而其实质后果很重——净收益数在三种设定下符号会翻转）；
分散重复的条件限定（几乎每个政策模拟结论旁重复一次）；不限定，把反事实写成弹性事实。

**最干净的分界标记：`as we model` / `Given the model structure`**——只出现在结构估计论文里，
用来标注"这个结论由模型设定决定而非由数据支持"。有一处作者因此**主动放弃解释该结论**：
"Given the model structure, the effect … should be consistent qualitatively. Therefore,
**we omit the repeated qualitative interpretation**."

**方法论断言的强度反常**：结构论文引言里最强的三句 T0 全都不是关于世界的，而是关于
别人方法的偏误。对自己的结论一律降到 T3。

---

## 六、对检查器的影响

四条新的可机器化检查，全部来自上面的判据：

| 检查 | 依据 | 输出级别 |
|---|---|---|
| **传导性**：某条 claim 在结果节收缩过（`revision_reason: bounded_by`），但摘要/结论/**标题**中同一 claim 的档位未跟随 | 判据 (b)；语料 30/45 组 | BLOCK |
| **即时回收**：让步结构后 1 句内出现 `However / Overall / Nevertheless / Encouragingly` 且主张档位未降 | 判据 (d)；14/14 篇有此模板 | WARN |
| **反证显著度**：针对识别假设的反证，其 prominence 低于"独立转折句 + 正文" | 8/14 篇把最重披露放在脚注/附录 | BLOCK |
| **过度声称残差**：措辞档位 − 证据强度（含 `underlying_precision`） > 0 | 6.10 | BLOCK（>0）/ INFO（<0） |

以及一条否定式断言的硬规则：**没有 `power_basis` 就不许写 "we rule out"**，只能写
"does not appear to be the primary driver"。
