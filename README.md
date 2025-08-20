# Intersection & Union of BED4 Intervals

A clean, dependency-free Python CLI for computing the **union** or **intersection** of two BED4 files.
Designed for clarity, explicit edge-case handling, and easy reuse in bioinformatics pipelines.

- **Input:** two whitespace-separated BED4 files with columns: `chrom  start  end  name`
- **Output:** a BED4 file you specify
- **Operations:** `union` (merge by feature name within a chromosome), `isec` (pairwise interval overlap per chromosome)
- **Python:** 3.8+

> Note: BED is typically **0-based, half-open**; chromosome labels must match exactly (e.g., `chr1` vs `1` are different).

---

## Motivation

**Goal** Read two BED4 files and, based on user choice, compute **either** the union **or** the intersection.

**Intersection (Isec):**
Report **all non-empty overlaps** between each interval in file 1 and each interval in file 2 **on the same chromosome**.

Overlap rule (half-open intervals): [a,b) and [c,d) overlap iff a < d **and** c < b.

Example: [30,50) & [50,70) → **no overlap**

Example: [30,52) & [50,70) → **overlap** [50,52)

The feature name in the output is taken from file 1.

**Union (union):**
Output **all features** that occur in at least one file.

If a feature name occurs in only one file → include as-is.

If a feature name occurs in **both** files on **different chromosomes** → exclude both.

If a feature name occurs in **both** files on the **same chromosome** → output a single interval using the smallest covering span of both:

[30,40) + [70,90) → [30,90)

[30,50) + [40,45) → [30,50)

**CLI contract (argparse)**

operation (union or isec)

input1 path

input2 path

output path

The order of output lines is not important.

---

## Quick Start

```bash
# Union (merge by feature name if on the same chromosome)
python mycode.py union main.bed.txt unionsecondfile.bed.txt union_results.bed.txt
cat union_results.bed.txt

# Intersection (interval overlap by chromosome; name is taken from file1)
python mycode.py isec  main.bed.txt intersectionsecondfile.bed.txt isec_results.bed.txt
cat isec_results.bed.txt

# CLI help
python mycode.py -h

---
---

## Features included

**Robust parsing** 

Skips blank lines and # comments

Accepts whitespace-separated columns (tabs or spaces)

Auto-swaps inverted intervals (start > end)

Defaults name to . if the 4th column is missing

Union

Groups intervals by name across both files

Merges only when intervals with the same name are on the same chromosome

Flags & drops “same name but different chromosome”

Intersection

Checks pairwise overlaps by chromosome (no requirement to match names)

Output name is inherited from the file1 interval

Clear output & errors

Summary stats printed to stdout

Warnings/parse errors printed to stderr (with line numbers)
