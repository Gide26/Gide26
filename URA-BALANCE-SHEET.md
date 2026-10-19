# URA Income Tax Working Template — balance sheet and income statement

A single-file, offline HTML template for preparing the **statement of income and expenditure** and
the **statement of assets and liabilities** that must accompany a Ugandan income tax return for a
business run by an individual (sole trader).

**File:** [`ura-balance-sheet.html`](ura-balance-sheet.html) — open it in any browser. No install,
no internet connection, no data leaves your machine.

---

## Why this exists

Section 118(5) of the Income Tax Act (Cap. 340) says:

> *"A return of income of a taxpayer who is carrying on business shall be accompanied by a statement
> of income and expenditure and a statement of the assets and liabilities of the taxpayer."*

For a sole trader that statement is filed on **form DT-2001 — Income Tax Return for Individual with
Business Income**, or on **form DT-2003** when it is a *provisional* return. This template helps you
build both statements, check the balance sheet balances, and then transfer the figures into the
official URA Excel template.

**It is not the return.** You still download DT-2001 (or DT-2003) from the URA portal, type your
figures in, validate and upload it. This is your working paper and the supporting statement that
goes with it.

---

## What it does

| Feature | Detail |
|---|---|
| **Four tabs** | Balance Sheet · Income Statement · Assets Register · Checklist & Guidance. |
| **Auto-totals** | Every subtotal, the net current assets figure, total assets, total liabilities and owner's funds are calculated as you type. |
| **Balance check** | A red/green panel tells you immediately whether assets equal liabilities plus capital — and if not, lists the usual causes. |
| **Live ratios** | Current ratio, gearing and net current assets, for the questions a tax officer is likely to ask. |
| **URA line references** | Every balance sheet line carries its Section E reference (toggle "URA line refs" in the toolbar) so you can map figures line-for-line onto the official form. |
| **Rate-and-period expenses** | On the Income Statement you type the *rate* you pay and whether it is per day, per month or per year. The sheet annualises it and shows the monthly equivalent so you can check it against what you actually pay. |
| **Automatic tax** | Chargeable income, tax under the correct band set, net profit after tax, and the four provisional tax instalments. |
| **One source of truth** | Net profit after tax flows into owner's funds (line E9b) and the tax charge flows into the provision for income tax (line E3diia). The two statements can never disagree. |
| **Assets register** | A separate tab with an itemised fixed asset list and a tax depreciation class per item, reconciled automatically against the balance sheet. |
| **Autosave** | Your figures are saved in your browser as you type, and restored when you come back. |
| **Export** | Both statements as one CSV, the register as CSV, and a full JSON backup you can restore later. |
| **Print / PDF** | A clean A4 layout via the browser's print dialog, with the taxpayer details and a proper statement heading on every statement. |

Your figures are stored only in this browser's local storage. Nothing is uploaded anywhere.

---

## How to use it

1. **Taxpayer details** — business name, owner, TIN, year of income, currency, who prepared it.
2. **Income Statement tab** — turnover, cost of sales, other income, operating expenses, tax.
3. **Balance Sheet tab** — assets column, then liabilities & owner's funds column.
4. **Owner's capital** — the template works it out for you:
   `opening capital + net profit for the year (after tax, from the Income Statement) + capital
   introduced − drawings`. If you already know the closing capital, tick *Override* and type it in.
5. **Check the balance panel.** If it is red, work down the list of common causes.
6. **Assets Register tab** — list each fixed asset, and use the reconciliation panels to confirm the
   register agrees with the balance sheet.
7. **Print or export**, then transfer the figures into DT-2001 or DT-2003.

### Entering your expenses: rate and period

This is the part people get wrong by hand. For every operating expense, type the **rate** you pay
and choose **how often** you pay it. The sheet does the multiplication, and shows you the monthly
equivalent next to it so you can check it against your bank or cash book.

| You pay | Enter as | Rate | Period | Sheet works out |
|---|---|---|---|---|
| Food for two people, every day | per day | 10,000 | per day | 3,650,000 a year · 304,167 a month |
| Transport, every day | per day | 40,000 | per day | 14,600,000 a year · 1,216,667 a month |
| Rent | per month | 1,780,000 | per month | 21,360,000 a year · 1,780,000 a month |
| Rubbish collection | per month | 20,000 | per month | 240,000 a year · 20,000 a month |
| Casual labour / cleaning | per day | 30,000 | per day | 10,950,000 a year · 912,500 a month |
| Repairs | per month | 350,000 | per month | 4,200,000 a year · 350,000 a month |
| Marketing | per month | 300,000 | per month | 3,600,000 a year · 300,000 a month |

*365 days and 12 months per year are set at the top of the Income Statement tab — change them if
your year of income is not a normal one.*

**Rules of thumb**

- Repairs that merely *maintain* an asset are deductible expenses. Repairs that *improve or extend*
  it are capital — put them in fixed assets on the Balance Sheet tab instead.
- Food and staff welfare are deductible if they are for the business. Anything for you personally
  is a drawing, not an expense.
- Rent paid up to date means **no** prepayment on the balance sheet and **no** rent creditor.
- Anything you paid for but have not yet used up is a prepayment (current asset). Anything you have
  used but not paid for is a creditor.

### If the statement does not balance

In practice it is nearly always one of these:

- Net profit for the year is missing or does not agree with your income statement.
- Drawings are understated — money taken for personal use reduces capital, it is not an expense.
- Capital introduced during the year has not been added back.
- A liability is missing — unpaid VAT, PAYE, NSSF, a tax provision, a loan instalment, or an amount
  owing to URA (the *Balance with URA* line).
- An asset is missing — stock counted but not valued, or a fixed asset bought on credit that is also
  missing from creditors.
- Accumulated depreciation is out of step with the capital allowance claimed in the income statement.
- Goods on hire purchase recognised only in part — both the asset and the outstanding liability
  need to appear.

---

## Provisional income tax — year of income 1 July 2026 to 30 June 2027

If you are filing a **provisional** return (form DT-2003), the income statement figures are your
**estimates** for the year. You may file an amended provisional return at any time before the year of
income ends if your figures change, and the final return (DT-2001) replaces the estimate with
actual figures.

| What | When |
|---|---|
| Provisional return (DT-2003) for an individual | Within the first 3 months of the year of income — by **30 September 2026** |
| 1st instalment — 25% of the estimated tax | **30 September 2026** |
| 2nd instalment — 25% | **31 December 2026** |
| 3rd instalment — 25% | **31 March 2027** |
| 4th instalment — 25% | **30 June 2027** |
| Amended provisional return | Any time before **30 June 2027** |
| Final return (DT-2001) with actual figures | Within 6 months of the year of income ending — by **31 December 2027** |

Individuals pay provisional tax in **four equal instalments of 25%** of the estimated annual tax
(ITA s.121), due on the last day of the 3rd, 6th, 9th and 12th month of the year of income.

A provisional return filed after 30 September 2026 still attracts the late filing penalty of
UGX 200,000 or 2% of the tax liability, whichever is higher, and the instalments remain due on
their dates even if the return is late.

---

## Individual income tax bands

The **Income Tax (Amendment) Act 2026** took effect on **1 July 2026**, so it applies in full to
the year of income 1 July 2026 – 30 June 2027. The template is set to the new bands; switch to the
previous bands at the top of the Income Statement tab if you are preparing an earlier year.

| Chargeable income (UGX) | New bands (from 1 July 2026) | Previous bands (to 30 June 2026) |
|---|---|---|
| Up to 4,020,000 | Nil | — |
| Up to 2,820,000 | — | Nil |
| 2,820,000 – 4,020,000 | — | 10% of the excess over 2,820,000 |
| 4,020,000 – 4,920,000 | 20% of the excess over 4,020,000 | 120,000 + 20% of the excess over 4,020,000 |
| 4,920,000 – 5,820,000 | 180,000 + 25% of the excess over 4,920,000 | — |
| 5,820,000 – 120,000,000 | 405,000 + 30% of the excess over 5,820,000 | 300,000 + 30% of the excess over 4,920,000 |
| Over 120,000,000 | as above, plus 10% of the excess over 120,000,000 | as above, plus 10% of the excess over 120,000,000 |

The nil band was raised from UGX 2,820,000 to UGX 4,020,000, the 10% band was replaced by 20%, and
a new 25% band was inserted. The effective top rate above UGX 120,000,000 is 40%.

---

## Line-item structure

The balance sheet layout follows the URA income tax return taxonomy (Section E), so figures
transfer line for line.

| This template | URA Section E |
|---|---|
| 1. Fixed assets — a to f | E) 1) a–f |
| Total cost of fixed assets | E) 1) g |
| Less: accumulated depreciation | E) 1) h |
| Net book value of fixed assets | E) 1) i |
| 2. Investments | E) 2) a–e |
| Total investments | E) 2) f |
| 3. Current assets — stock, receivables, balances, other | E) 3) a) i–iv |
| Loans and advances | E) 3) b) i–vi |
| Total current assets | E) 3) c |
| 5. Current liabilities | E) 3) d) i) a–e |
| 6. Provisions | E) 3) d) ii) a–d |
| Total current liabilities and provisions | E) 3) d |
| 4. Deferred tax asset | E) 4 |
| **TOTAL ASSETS** | E) 5 |
| 7. Loan funds — secured and unsecured | E) 7) a) i–v, b) i–v |
| Total loan funds | E) 7) c |
| 8. Deferred tax liability | E) 8 |
| 9. Owner's funds | E) 6), adapted for a sole trader |
| Total equity and long-term liabilities | E) 9 |

In the URA form for a non-individual, E) 6) is shareholders' funds (share capital, reserves, retained
earnings). A sole trader has no share capital, so section 9 here uses owner's capital instead. The
company-only lines have no equivalent for an individual and should be left blank on the return.

The income statement follows the conventional sequence — turnover, cost of sales, gross profit,
other income, operating expenses, profit before tax, chargeable income, tax, net profit — and does
**not** carry invented URA line numbers, because the published line-item list for the income
statement section of the return could not be verified.

---

## Tax depreciation classes — ITA Schedule 7, Part I

Use these to work out accumulated depreciation and to cross-check the capital allowance claimed in
your income statement. The deduction is written-down value × rate (ITA s.27).

| Class | Assets included | Rate |
|---|---|---|
| 1 | Computers and data handling equipment | 40% |
| 2 | Plant and machinery used in farming, manufacturing and mining | 30% |
| 3 | Automobiles; buses, minibuses, goods vehicles; construction and earth moving equipment; specialised trucks, tractors, trailers; rail cars and locomotives; vessels, barges, tugs and similar water transport; aircraft; specialised public utility plant and equipment; office furniture, fixtures and equipment; any depreciable asset not in another class | 20% |
| Industrial buildings | Industrial buildings, approved hotels, approved hospitals, approved commercial buildings — straight line, apportioned for days of use (ITA s.28) | 5% |

Depreciable asset classes were reduced from four to three with effect from 1 July 2021, and the initial
allowances previously available on new business assets and industrial buildings were removed from
1 July 2023. Confirm the current position against the Act as amended, or with your tax adviser, before
finalising.

---

## Filing it with URA

1. Download **DT-2001** (final) or **DT-2003** (provisional) from the URA portal:
   <https://ura.go.ug/en/download/dt-2001-income-tax-return-form-for-individual-with-business-income/>
   (or via e-Services → e-Returns → select the return period).
2. Open it and **enable macros / content**. URA warns you must not cut and paste values into the
   sheet — type them into the cells.
3. Complete the taxpayer details, income statement, and this statement of assets and liabilities.
4. Click **VALIDATE** on the last page and fix anything on the error sheet.
5. Generate the upload file, log back in, and upload under **e-Services → Return → File a return →
   Tax final** (or *Tax provisional*). Do not rename the file.
6. Attach these statements and the assets register.
7. Pay the tax due by the same deadline.

**Deadlines**

| Return | Form | Due |
|---|---|---|
| Provisional income tax (individual) | DT-2003 | Within 3 months of the start of the year of income — normally 30 September |
| Final income tax (individual with business income) | DT-2001 | Within 6 months after the year of income ends — 30 June for a calendar year, 31 December for a 1 July–30 June year |
| Amended provisional return | DT-2003 | By 30 June |

**Penalties and record keeping**

- Late filing: UGX 200,000 or 2% of the tax liability, whichever is higher.
- Turnover of UGX 500,000,000 or more: audited financial statements prepared by a member of the
  Institute of Certified Public Accountants of Uganda must accompany the return (Tax Procedures
  Code Act s.16(5)).
- Keep sales invoices and EFRIS e-invoices/e-receipts, purchase invoices, bank and mobile money
  statements, payroll records, the assets register, stock records and the filed return for **5 years**
  after the end of the tax period.

---

## Sources

- Income Tax Act, Cap. 340 — s.118(5) (statement of income and expenditure and assets and
  liabilities), s.121 (provisional tax instalments), s.122 (estimate of chargeable income),
  s.27 (depreciation), s.28 (industrial buildings), Schedule 7 Part I (depreciation classes),
  Part II (vehicle ceiling), Part III (industrial buildings).
- **Income Tax (Amendment) Act 2026** — new Schedule 4 Part I resident-individual bands with effect
  from 1 July 2026 (nil band UGX 4,020,000; 20% band; new 25% band; 30% band; 10% surcharge above
  UGX 120,000,000). Assented 20 August 2026.
- Tax Procedures Code Act — s.16(5) (audited financial statements), record-keeping requirements.
- URA return forms: DT-2001 (individual with business income), DT-2002 (non-individual),
  DT-2003 (provisional, individual), DT-2004 (provisional, non-individual), DT-2005 (partnership).
- URA *Ask the Commissioner General* filing-date table — individual provisional and final return
  deadlines.
- Line-item structure follows Section E of the URA non-individual income tax return, as documented in
  UNU-WIDER, *The Uganda Revenue Authority firm panel* (Technical Note 2022/2).

---

**This is a working aid, not a URA form and not tax advice.** Verify the figures and the current law
before you file. If you are unsure about a figure, ask your tax adviser or your URA tax officer.
