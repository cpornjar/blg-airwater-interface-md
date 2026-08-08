mol new /Users/mac2022-1/Workspace/MILK_FROTHING/inputs_CAS/CASEIN_mature_phospho_SP2.pdb
mol delrep 0 top

# same amber as calyx = plot_style.py COLORS["patch"] #B35806, exact RGB match
color change rgb 3 0.702 0.345 0.024
color change rgb 6 0.75 0.75 0.75

mol representation NewCartoon
mol color ColorID 6
mol selection "protein and not (resid 1 to 25)"
mol material AOChalky
mol addrep top

mol representation NewCartoon
mol color ColorID 3
mol selection "protein and resid 1 to 25"
mol material AOChalky
mol addrep top

mol representation Licorice 0.35
mol color ColorID 3
mol selection "protein and resid 1 to 25"
mol material AOChalky
mol addrep top

display projection Orthographic
display depthcue off
display shadows off
display ambientocclusion on
color Display Background white
axes location Off
display resetview
scale by 1.25

render TachyonInternal /Users/mac2022-1/Workspace/MILK_FROTHING/results/figures/render/cas_patch_raw.png

quit
