import matplotlib.pyplot as plt

# Data
# initial_line_coverage = [94, 90, 92, 85, 78]
# initial_branch_coverage = [16, 16, 16, 16, 16]
# improved_line_coverage = [98, 94, 97, 91, 85]
# improved_branch_coverage = [16, 16, 16, 16, 16]

initial_line_coverage = [59, 49, 49, 48, 46]
initial_branch_coverage = [21, 21, 21, 21, 21]
improved_line_coverage = [79, 79, 79, 77, 77]
improved_branch_coverage = [21, 21, 21, 21, 21]

# Create a figure and axis object
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))

# Create box plots for line coverage
axes[0].boxplot([initial_line_coverage, improved_line_coverage], labels=['Initial', 'Improved'])
axes[0].set_title('Line Coverage')
axes[0].set_ylabel('Coverage (%)')

# Create box plots for branch coverage
axes[1].boxplot([initial_branch_coverage, improved_branch_coverage], labels=['Initial', 'Improved'])
axes[1].set_title('Branch Coverage')
axes[1].set_ylabel('Coverage')

# Show the plot
plt.tight_layout()
plt.show()
