from tabulate import tabulate

# Create a list of lists with the data for your table
data = [    ["0", "0.0725", "n/a"],
    ["0.2", "0.0693", "0.0879"],
    ["0.4", "0.0832", "0.0928"],
    ["0.6", "0.0703", "0.0880"],
    ["0.8", "0.0635", "0.0781"],
    ["1", "0.0652", "0.0896"],
]

# Define the headers for your table
headers = ["p", "query", "trade"]

# Use the tabulate function to generate the table
table = tabulate(data, headers, tablefmt="grid")

# Print the table
print("Test result without caching")
print(table)

