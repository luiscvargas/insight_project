def get_oauth_data(website):
	if website == "yelp":
		with open("../oauth_keys/yelp.keys") as f:
			key1 = f.readline().split()[1]
			key2 = f.readline().split()[1]
			key3 = f.readline().split()[1]
			key4 = f.readline().split()[1]

		return (key1, key2, key3, key4)

	else:
		raise ValueError
		return (-1, -1, -1, -1)