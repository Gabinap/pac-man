# pac-man
faut mettre du son en sah
Pouvoir selectionner une difficulte (easy, normal, hard etc)
view pour la game 

Dans les parametres avant le jeu on doit aussi pouvoir choisir le player quon veut ainsi que les ghosts (Il faudra les representer par des gif), choisir lambiance quon veut (default (le niveau en json), ou un precise), Si on laisse les animations des models, le song des entites (comme dans un vrai jeu avec des cases a cocher et/ou un pourcentage a definir) avec des sections pour le song, le visuel, les commandes.

ghost 4 est un oeil avec des anneaux qui tournent autour, actuellement aucun anneau ne tourne et la texture de loeil est cassee, en revanche ce qui englobe loeil bouge et la texture du coutour ainsi que des anneaux fonctionne (cest la meme). Jai ces infos a lexecution:
:char(error): Could not find joint Bone.004.l_015 within the character hierarchy.
:char(error): Could not find joint Bone.006.L_07 within the character hierarchy.
:char(error): Could not find joint Bone.006.L_07 within the character hierarchy.
:char(error): Could not find joint Bone.004.l_015 within the character hierarchy.

ghost 5 est un monstre gris a deux pates qui marche, la texture globale de sa peau est correcte mais cest comme sil laissait des traces, certaines parties de ses pieds, tete, dos, queue sont statiques alors que tout le corps bouge ce qui rend un effet incomplet et qui "laisse des traces". Aussi jai ces info:
:char(error): Could not find joint Arm.l.001_08 within the character hierarchy.
:char(error): Could not find joint Arm.l_07 within the character hierarchy.
:char(error): Could not find joint Arm.l.002_09 within the character hierarchy.
:char(error): Could not find joint Arm.l.004_011 within the character hierarchy.
:char(error): Could not find joint Arm.l.003_010 within the character hierarchy.
:char(error): Could not find joint Arm.l.005_012 within the character hierarchy.
:char(error): Could not find joint Arm.r_013 within the character hierarchy.
:char(error): Could not find joint Spine.002_02 within the character hierarchy.
:char(error): Could not find joint Spine.001_01 within the character hierarchy.
:char(error): Could not find joint Spine_00 within the character hierarchy.
:char(error): Could not find joint Spine.003_03 within the character hierarchy.
:char(error): Could not find joint Spine.004_04 within the character hierarchy.
:char(error): Could not find joint Lowe_Mouth_06 within the character hierarchy.
:char(error): Could not find joint Lower Mouth_05 within the character hierarchy.
:char(error): Could not find joint Tail_019 within the character hierarchy.
:char(error): Could not find joint Tail.001_020 within the character hierarchy.
:char(error): Could not find joint Tail.002_021 within the character hierarchy.
:char(error): Could not find joint Tail.003_022 within the character hierarchy.
:char(error): Could not find joint Tail.004_023 within the character hierarchy.
:char(error): Could not find joint Tail.005_024 within the character hierarchy.
:char(error): Could not find joint Tail.006_025 within the character hierarchy.
:char(error): Could not find joint Tail.007_026 within the character hierarchy.
:char(error): Could not find joint Tail.008_027 within the character hierarchy.
:char(error): Could not find joint Arm.r.003_016 within the character hierarchy.
:char(error): Could not find joint Arm.r.002_015 within the character hierarchy.
:char(error): Could not find joint Arm.r.004_017 within the character hierarchy.
:char(error): Could not find joint Arm.r.005_018 within the character hierarchy.
:char(error): Could not find joint Arm.r.001_014 within the character hierarchy.
:char(error): Could not find joint Lower Mouth_05 within the character hierarchy.
:char(error): Could not find joint Lowe_Mouth_06 within the character hierarchy.

ghost 6 est un poisson, seule la texture de ses deux yeux nest pas chargee et ses yeux ne bougent pas. Le reste est parfait. Aussi voici dautres info:
:char(error): Could not find joint SideFin.L.005_017 within the character hierarchy.
:char(error): Could not find joint SideFin.L.004_016 within the character hierarchy.
:char(error): Could not find joint SideFin.L.005_017 within the character hierarchy.
:char(error): Could not find joint SideFin.L.004_016 within the character hierarchy.

CALIBUR est une armure, ses bras et jambes ont parfaits, en revanche son torse et son arme sont static et ne suivent pas les animations. Les textures sont donc correctes, le seul probleme etant le torse et larme qui sont statics. Aussi voici ce que lon a a lexecution:
:char(error): Could not find joint LowerArm.R_010 within the character hierarchy.
:char(error): Could not find joint LowerArm.L_07 within the character hierarchy.
:char(error): Could not find joint Hand.R_023 within the character hierarchy.
:char(error): Could not find joint Hand.L_017 within the character hierarchy.
:char(error): Could not find joint UpperLeg.R_013 within the character hierarchy.
:char(error): Could not find joint UpperLeg.L_011 within the character hierarchy.
:char(error): Could not find joint Knee.R_014 within the character hierarchy.
:char(error): Could not find joint Knee.L_012 within the character hierarchy.
:char(error): Could not find joint LowerArm.R_010 within the character hierarchy.

Les models 1 et 7 crash mais 0 2 3 sont parfait
