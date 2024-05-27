# Table of Contents

- [Table of Contents](#table-of-contents)
- [MLOps](#mlops-course-tasks)
- [Contributing](#contributing)

# MLOps Course Tasks
## [Methodology chosen][2]
[Data Science Lifecycle Process][1].
See [Branch Types][3] for branching naming model.

## Tasks
Tasks completed during MLOps course.

1. Block1: only Lectures.
2. [Block2](https://gitlab.com/DeadlySquad13/MlOps_course/-/tree/block2?ref_type=tags): GitLab repo with packages and basic checks + testing. 
3. [Block3](https://gitlab.com/DeadlySquad13/MlOps_course/-/tree/block3?ref_type=tags): modern package management via `pixi` and `Docker`
    support for future CI/CD checks.
4. [Block4](https://gitlab.com/DeadlySquad13/MlOps_course/-/tree/block4?ref_type=tags): CI/CD, gitlab docker registry, small EDA.

For easier introspection into what was done in span of course the
`block#_changes-short-description` branches are made and then the last commit
is tagged (see numbered list above).

If working in data science workflow, Data Science Lifecycle Process branches
are used with `block#_` instead of issue number. For example,
experiment and model branches made during block3 will be:
`experiment/block3_classification-EBM`
`model/block3_custom-churn-classification`

## Contributing
See guidelines in [Contributing](./CONTRIBUTING.md). This projects also
has Docker support, see ["Running in Docker"
section in Contributing](./CONTRIBUTING.md#running-in-docker).

## References
[1]: <https://github.com/dslp/dslp> 'Data Science Lifecycle Process'
[2]: <https://youtu.be/nx1VQrGfU8A?t=556> 'Data Science Lifecycle Process
Lecture'
[3]: <https://github.com/dslp/dslp/blob/main/branching/branch-types.md> 'Data
Science Lifecycle Branch Types'
