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

import math

from absl.testing import absltest
from absl.testing import parameterized

import futs

class FutsTest(parameterized.TestCase):

  def test_compute_rank_scores(self):
    nodes = [
        futs.Node(
            index=0,
            parent_index=None,
            solution=futs.Solution(""),
            score=1.0,
        ),
        futs.Node(
            index=1,
            parent_index=0,
            solution=futs.Solution(""),
            score=3.0,
        ),
        futs.Node(
            index=2,
            parent_index=0,
            solution=futs.Solution(""),
            score=2.0,
        ),
    ]
    futs.compute_rank_scores(nodes)
    self.assertEqual(nodes[0].rank_score, 0.0)
    self.assertEqual(nodes[1].rank_score, 1.0)
    self.assertEqual(nodes[2].rank_score, 0.5)

  def test_compute_pucts(self):
    nodes = [
        futs.Node(
            index=0,
            parent_index=None,
            solution=futs.Solution(""),
            score=1.0,
            rank_score=0.0,
            num_visits=1,
        ),
        futs.Node(
            index=1,
            parent_index=0,
            solution=futs.Solution(""),
            score=3.0,
            rank_score=1.0,
            num_visits=4,
        ),
        futs.Node(
            index=2,
            parent_index=0,
            solution=futs.Solution(""),
            score=2.0,
            rank_score=0.5,
            num_visits=0,
        ),
    ]
    futs.compute_pucts(nodes, c_puct=1.0)
    self.assertAlmostEqual(nodes[0].puct, 0 + 1 / 3 * math.sqrt(5) / (1 + 1))
    self.assertAlmostEqual(nodes[1].puct, 1 + 1 / 3 * math.sqrt(5) / (1 + 4))
    self.assertAlmostEqual(nodes[2].puct, 0.5 + 1 / 3 * math.sqrt(5) / (1 + 0))

  def test_backpropagate_visit(self):
    nodes = [
        futs.Node(
            index=0,
            parent_index=None,
            solution=futs.Solution(""),
            score=1.0,
        ),
        futs.Node(
            index=1,
            parent_index=0,
            solution=futs.Solution(""),
            score=2.0,
        ),
        futs.Node(
            index=2,
            parent_index=0,
            solution=futs.Solution(""),
            score=3.0,
        ),
    ]
    futs.backpropagate_visit(nodes, nodes[2])
    self.assertEqual(nodes[0].num_visits, 1)
    self.assertEqual(nodes[1].num_visits, 0)
    self.assertEqual(nodes[2].num_visits, 1)

  def test_search(self):
    problem = futs.Problem("Maximize version")
    initial_solution = futs.Solution("v0")
    initial_score = 0.0

    # Mock generator that just increments a version number in the program string
    def generate_fn(unused_problem, parent_solution, unused_parent_score):
      v = int(parent_solution.program[1:])
      return futs.Solution(f"v{v + 1}")

    # Mock executor that returns the version number as the score
    def execute_fn(unused_problem, solution):
      return float(int(solution.program[1:]))

    best_solution, best_score = futs.search(
        problem=problem,
        initial_solution=initial_solution,
        initial_score=initial_score,
        generate_fn=generate_fn,
        execute_fn=execute_fn,
        num_iterations=5,
        c_puct=1.0,
    )

    # With 5 iterations, we expect to see v1, v2, v3, v4, v5.
    # The best score should be 5.0 and solution v5.
    self.assertEqual(best_solution.program, "v5")
    self.assertEqual(best_score, 5.0)


if __name__ == "__main__":
  absltest.main()
