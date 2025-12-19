# CampLogic - Camp Grouping & Counselor Assignment Solver

This project is a constraint-based scheduling system for assigning campers and counselors into balanced summer camp groups. The solver enforces hard constraints (pairings, avoidance, attendance, staffing limits) and optimizes soft preferences (friends together, language matches, age preferences, gender balance).

The system is designed for summer camp scheduling with separate morning and afternoon sessions.

## Project Overview

This solver works in three main phases:

1. Data Parsing
- Reads camper and counselor data from CSV files
- Normalizes values, handles missing data, and builds structured objects
2. RBL (Rule-Based Logic) Construction
- Applies hard constraints using union-find clustering
- Builds valid group domains for each camper cluster and counselor
3. Constraint Satisfaction + Weighted Objective Evaluation
- Uses backtracking with heuristics (MRV, early pruning)
- Assigns campers to groups first, then counselors
- Scores the final solution using weighted soft preferences

## File Descriptions

***main.py*** - Entry point for the program

Loads data, builds constraints, runs the solver, prints group assignments, and outputs the final weighted score


***parsing.py*** - Handles CSV parsing and data cleaning

Used to load campers.csv and counselors.csv


***data_structures.py*** - Defines core data models and shared structures


***rbl.py*** - Builds the Rule-Based Logic layer

This phase filters impossible assignments early before solving. It counts attendance by session and determines the number of valid groups. It also builds camper and counselor eligibility domains and enforces hard constraints.


***cs_solver.py*** - Implemented the Constraint Satisfaction Solver

This ensures all hard constraints are satisfied before optimization. It includes a backtracking search with MRV heuristic. It features group size constraints, grade band width control and counselor feasibility checks.


***weighted_objective_function.py*** - Scores the final solution using soft constraints

Scoring includes counselor preferred age group matches, language matches between campers and counselors, friend placement, gender balance per group and pair-with bonuses and avoid-with penalties. It produces a total weighted score and detailed breakdowns for counselors and campers.

## How To Run on VS Code
1. Create a project folder and place all files in the same folder
2. Open the folder in VS Code
3. Install dependencies

**pip install pandas**

4. Run the program in terminal

**python main.py**

## Output

The program prints
- group assignments (campers + counselors)
- Camper grades per group
- Final weighted score
- Optional detailed scoring breakdowns (commented in main.py)

