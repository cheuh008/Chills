

# Importing ur own Assets

use `convert_mesh.py` provided by IsaacLab to run the following the the cwd `assets\`

in your IsaacLab enviorment (ie env_isaaclab) run `python convert_mesh.py <filename.obj>  "<desireed_name>\<desireed_name>.usd" --make-instanceable --collision-approximation convexDecomposition --mass 0.2` `

for example 

```bash
python convert_mesh.py beaker.obj  "beaker\beaker.usd" --make-instanceable --collision-approximation convexDecomposition --mass 0.2
python convert_mesh.py con_flask.obj  "con_flask\con_flask.usd" --make-instanceable --collision-approximation convexDecomposition --mass 0.2
python convert_mesh.py round_bot.obj  "round_bot\round_bot.usd" --make-instanceable --collision-approximation convexDecomposition --mass 0.2
```
