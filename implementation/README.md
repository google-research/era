# Flat UCB Tree Search (FUTS)

This is a generic single-threaded reference implementation of the Tree Search
algorithm that is described in Algorithm 1 of
[Aygün, et al., 2025](https://arxiv.org/abs/2509.06503).

The `search` function requires concrete implementations of two functions:

1. `generate_fn`: This function takes the problem definition and a past
   solution, and generates a new (ideally improved) solution. An actual
   implementation should render a prompt out of the problem description and the
   past solution, feed it to an LLM, and parse the new solution from the LLM's
   response.

2. `execute_fn`: This function takes the problem definition and a candidate
   solution, and assigns a score to the solution in the context of the problem.
   An actual implementation should run the solution in a sandboxed environment
   where all the necessary libraries and data (e.g. training dataset) is
   available, take the generated outputs and evaluate them against the problem
   (e.g. against a test dataset).

Once these functions are provided, the `search` function will iterate
`num_iterations` times, expanding a search tree one node at a time using the
Flat UCB algorithm. When it finishes, it will return the best solution found.

## Citing This Work

If you use the code or data in this package, please cite:

```bibtex
 @misc{aygün2025aihelpscientistswrite,
      title={An AI system to help scientists write expert-level empirical software}, 
      author={Eser Aygün and Anastasiya Belyaeva and Gheorghe Comanici and Marc Coram and Hao Cui and Jake Garrison and Renee Johnston Anton Kast and Cory Y. McLean and Peter Norgaard and Zahra Shamsi and David Smalling and James Thompson and Subhashini Venugopalan and Brian P. Williams and Chujun He and Sarah Martinson and Martyna Plomecka and Lai Wei and Yuchen Zhou and Qian-Ze Zhu and Matthew Abraham and Erica Brand and Anna Bulanova and Jeffrey A. Cardille and Chris Co and Scott Ellsworth and Grace Joseph and Malcolm Kane and Ryan Krueger and Johan Kartiwa and Dan Liebling and Jan-Matthis Lueckmann and Paul Raccuglia and Xuefei and Wang and Katherine Chou and James Manyika and Yossi Matias and John C. Platt and Lizzie Dorfman and Shibl Mourad and Michael P. Brenner},
      year={2025},
      eprint={2509.06503},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2509.06503},
}
```
