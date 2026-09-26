from meep import mpb
ms = mpb.ModeSolver()
print("MPB methods:")
for m in dir(ms):
    if 'energy' in m.lower() or 'field' in m.lower() or 'confinement' in m.lower():
        print(" ", m)
