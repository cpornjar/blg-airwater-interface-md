mol new /Users/mac2022-1/Workspace/MILK_FROTHING/inputs_BLG/1BEB_A_clean.pdb
mol delrep 0 top

# amber for calyx = plot_style.py COLORS["calyx"] #B35806, exact RGB match
color change rgb 3 0.702 0.345 0.024
# neutral silver-grey for the rest of the fold
color change rgb 6 0.75 0.75 0.75

mol representation NewCartoon
mol color ColorID 6
mol selection "protein and not (resid 39 41 56 58 92 103 105 107 125)"
mol material AOChalky
mol addrep top

mol representation NewCartoon
mol color ColorID 3
mol selection "protein and resid 39 41 56 58 92 103 105 107 125"
mol material AOChalky
mol addrep top

mol representation Licorice 0.35
mol color ColorID 3
mol selection "protein and resid 39 41 56 58 92 103 105 107 125"
mol material AOChalky
mol addrep top

display projection Orthographic
display depthcue off
display shadows off
display ambientocclusion on
color Display Background white
axes location Off
display resetview
scale by 1.35

render TachyonInternal /Users/mac2022-1/Workspace/MILK_FROTHING/results/figures/render/blg_calyx_raw.png

quit
