# Copyright 2026 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generic implementation of the Flat Upper Confidence Bound (UCB) Tree Search algorithm.

The algorithm uses the polynomial formulation used in AlphaZero named Polynomial
Upper Confidence bounds applied to Trees (PUCT).
"""

import dataclasses
import math
from typing import Protocol, Optional, Union, List, Tuple


@dataclasses.dataclass(frozen=True)
class Problem:
  """Object that defines the problem to be solved."""

  description: str


@dataclasses.dataclass(frozen=True)
class Solution:
  """Object that defines a candidate solution to the problem."""

  program: str


@dataclasses.dataclass
class Node:
  """Node in the search tree."""

  index: int
  parent_index: Optional[int]
  solution: Solution
  score: float
  num_visits: int = 0
  rank_score: float = 0.5
  puct: float = 0.5


class Generate(Protocol):
  """Generates a new solution to the problem based on the parent solution."""

  def __call__(
      self, problem: Problem, parent_solution: Solution, parent_score: float
  ) -> Solution:
    ...


class Execute(Protocol):
  """Executes the solution against the problem and returns its score."""

  def __call__(self, problem: Problem, solution: Solution) -> float:
    ...


def compute_rank_scores(nodes: List[Node]) -> None:
  """Computes and updates the rank scores of the nodes."""
  if len(nodes) == 1:
    nodes[0].rank_score = 0.5
    return
  sorted_nodes = sorted(nodes, key=lambda n: n.score)
  for rank, node in enumerate(sorted_nodes):
    node.rank_score = rank / (len(sorted_nodes) - 1)


def compute_pucts(nodes: List[Node], c_puct: float) -> None:
  """Computes and updates the PUCTs of the nodes."""
  prior = 1 / len(nodes)
  total_num_visits = sum(n.num_visits for n in nodes)
  for node in nodes:
    node.puct = node.rank_score + c_puct * prior * math.sqrt(
        total_num_visits
    ) / (1 + node.num_visits)


def backpropagate_visit(nodes: List[Node], node: Node) -> None:
  """Backpropagates the visit to the node to its ancestors."""
  node.num_visits += 1
  if node.parent_index is not None:
    backpropagate_visit(nodes, nodes[node.parent_index])


def search(
    problem: Problem,
    initial_solution: Solution,
    initial_score: float,
    generate_fn: Generate,
    execute_fn: Execute,
    num_iterations: int,
    c_puct: float = 1.0,
) -> Tuple[Solution, float]:
  """Performs Flat UCB tree search on the problem.

  Args:
    problem: The problem to be solved.
    initial_solution: The initial solution to the problem.
    initial_score: The score of the initial solution.
    generate_fn: A function that generates a new solution to the problem based
      on the parent solution.
    execute_fn: A function that executes the solution against the problem and
      returns its score.
    num_iterations: The number of iterations to perform.
    c_puct: The exploration factor in the PUCT computation.

  Returns:
    The best solution found and its score.
  """
  # Initialize the search tree with a root node.
  nodes = [
      Node(
          index=0,
          parent_index=None,
          solution=initial_solution,
          score=initial_score,
      )
  ]

  for _ in range(num_iterations):
    # Compute rank scores and PUCTs.
    compute_rank_scores(nodes)
    compute_pucts(nodes, c_puct)

    # Select the node with largest PUCT.
    best_node = max(nodes, key=lambda n: n.puct)

    # Expand the selected node.
    new_solution = generate_fn(problem, best_node.solution, best_node.score)
    new_score = execute_fn(problem, new_solution)
    new_node = Node(
        index=len(nodes),
        parent_index=best_node.index,
        solution=new_solution,
        score=new_score,
    )
    nodes.append(new_node)

    # Backpropagate results.
    backpropagate_visit(nodes, new_node)

  # Return the best solution found and its score.
  best_node = max(nodes, key=lambda n: n.score)
  return best_node.solution, best_node.score