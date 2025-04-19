from flask import Flask, request, jsonify
from math import ceil
from itertools import permutations

app = Flask(_name_)

dist = {
    'C1-C2': 4, 'C2-C1': 4,
    'C1-C3': 5, 'C3-C1': 5,
    'C2-C3': 3, 'C3-C2': 3,
    'C1-L1': 3, 'C2-L1': 2.5, 'C3-L1': 2,
    'L1-C1': 3, 'L1-C2': 2.5, 'L1-C3': 2
}

catalog = {
    'A': ['C1', 3],
    'B': ['C1', 2],
    'C': ['C1', 8],
    'D': ['C2', 12],
    'E': ['C2', 25],
    'F': ['C2', 15],
    'G': ['C3', 0.5],
    'H': ['C3', 1],
    'I': ['C3', 2]
}

def cost(w, d):
    if w <= 5:
        return 10 * d
    extra = w - 5
    blocks = ceil(extra / 5)
    return d * (10 + blocks * 8)

def all_routes(centers):
    routes = []
    for perm in permutations(centers):
        n = len(perm)
        for m in range(2 ** n):
            r = []
            for i in range(n):
                r.append(perm[i])
                if (m >> i) & 1:
                    r.append('L1')
            r.append('L1')
            routes.append(r)
    return routes

def calc(order):
    weight = {'C1': 0, 'C2': 0, 'C3': 0}
    for pid, qty in order.items():
        if pid not in catalog:
            continue
        loc, w = catalog[pid]
        weight[loc] += qty * w

    needed = [c for c in ['C1', 'C2', 'C3'] if weight[c] > 0]
    routes = all_routes(needed)
    min_cost = float('inf')

    for r in routes:
        c = 0
        load = 0
        picked = set()

        for i in range(len(r) - 1):
            u, v = r[i], r[i + 1]

            if u in weight and u not in picked:
                load += weight[u]
                picked.add(u)

            if u == 'L1':
                load = 0

            d = dist.get(f"{u}-{v}")
            if d is not None:
                c += cost(load, d)

        min_cost = min(min_cost, c)

    return int(min_cost)

@app.route('/calculate', methods=['POST'])
def api():
    try:
        data = request.get_json()
        total = calc(data)
        return jsonify({"cost": total})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if _name_ == '_main_':
    app.run(debug=True)
