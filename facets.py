import logging

def build_facet_list(facet, base):
	if facet in base:
		logging.debug(f"removing {facet} from {base=}")
		base.remove(facet)
		logging.debug(f"{base=}")
		
		if not base:
			return base
		
		else:
			return ",".join(base)
	
	elif base:
		print(f"adding {facet} to {base=}")
		f = base.append(facet)
		logging.debug(f"{base=}")
		return ",".join(base)
	
	else:
		logging.debug(f"adding {facet} to empty {base=}")
		return facet


def build_query(facet: str, agg: str, query: str, tags: list, states: list) -> str:
	"""builds the query to toggle filters"""

	logging.debug(f"{tags=}", f"{states=}")
	
	if agg == "tags":
		tags = build_facet_list(facet, tags)
	
	if agg == "states":
		states = build_facet_list(facet, states)
	
	if all([tags, states]):
		return f"/search?q={query}&tags={tags}&states={states}"
	elif tags:
		return f"/search?q={query}&tags={tags}"
	elif states:
		return f"/search?q={query}&states={states}"
	else:
		return f"/search?q={query}"
