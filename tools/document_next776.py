"""Record the delivered two-level milestone while preserving earlier handoff history."""
from audit_scenes import ROOT
intro='''Public771, 2026-11-11: The Stampede and Simba's Exile practical resource
delivery is installed. Read [delivery, evidence and limits](stampede-exile-delivery.md).
Launch `Play Stampede MD.cmd` or `Play Simbas Exile MD.cmd`; separate settings,
existing Mix choices preserved. Actual CMDs775 pass with256/320 viewports.
New Stampede cub/rock frames, Wildebeest/canyon colors and start/collision sounds;
Exile's verified fixed/banded background, owned enemy/leaf/pickup art/colors,
shared effects plus rock sounds, roar14 and independent health-death movement/music.
Both-level route and final Exile continuation reach healthy Hakuna. Native
Stampede perspective geometry, most gameplay, unknown-art fallbacks and native
fall/final-life paths remain explicit; no universal MD parity claim.

Player: dist/installed-preview771/LionKing.exe;
SHA256:486963f8911a033e2d79352614d4478f0303cd3237ffce9544eb3eef5b28bcf2.
Helper741/default Setup imports1026 images and new1040-byte TLKNXT01 palettes;
all preceding973 images, old palettes/death bank and five gameplay sections
preserved. Sprite-v2 policy3, aggregate schema3/six sections;840 bounds unchanged.
773 qualifies focused checks;774 publishes and updates installed data;775
verifies both actual launchers/clients. New source code imports prepared data;
no runtime ROM-code decoder added. Current death save, sound isolation and retry
pass. No earlier-level replay/old-save migration or unrelated matrix was needed.
Do not resume748's slow private build or its per-pixel setting searches;751+
resolves choices per scanline/owner per piece. Original asset counts did not
prove actor coverage; use actual scene descriptors and initialized banks.
Next chronological level: Hakuna Matata (ID5), when requested. No active goal
was created by the two-level request.
'''
p=ROOT/'docs/HANDOFF.md';s=p.read_text();s=s.replace('# Lion King PC development handoff\n','# Lion King PC development handoff\n\n'+intro+'\n## Previous Graveyard delivery720\n',1);p.write_text(s)
p=ROOT/'docs/next-levels-status.md';p.write_text('CURRENT771: Stampede/Exile delivery installed.\n\n'+intro+'\nEarlier dated status follows.\n\n'+p.read_text())
p=ROOT/'docs/background-audit.md';p.write_text(p.read_text()+'''
## The Stampede and Exile delivery771

See [delivery evidence](stampede-exile-delivery.md). Exile initializer08C1C8,
update08C26E and table08C17A use a fixed152-line section followed by8/16/24/24
lines at1/16,1/8,1/4,1/2 X; Y=0. Four actual original captures have complete
matching base tiles/names; native C sampler749 matches286720 VDP pixel tokens.
Saved raster-camera history owns the phase; the MD background readiness now
includes actual Exile4. Foreground/colors remain separate.

Stampede retains native Mode1 perspective geometry, with original MD canyon
colors and an explicit matte-slot correspondence. H32 means256 columns. Its
generic decoded scene descriptor is not a complete MD perspective renderer;
background readiness still excludes3. This delivery does not equate semantic
planes across versions. Actual installed Windows clients775 verify both scenes.
''')
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''
### Stampede/Exile725..776: practical next-two-level delivery

'''+intro+'''
Implementation: tlk_next_scene_data prepares original MD palettes plus native
palette identities; sixth installed aggregate section, no runtime ROM decode.
Stampede special lines use existing Mode1 compositor,53 reviewed frame links
and shared80-pose Wildebeest art. Native opaque matte slot31 maps to MD black,
avoiding an incorrect nearest red. Exile links actual owned enemy/leaf/pickup
families to existing reviewed mappings and scene palettes; its native renderer
gate was the missing feature. Extend shared cub health-death presentation and
music ownership to actual Exile descriptor44F; current save and native/MD audio
controls pass. New rock-controller FM165 sites are source-confirmed, not inferred
from event counts. Shared roar/leaf/chameleon hooks retain exact owner checks.
Build integration includes next_scene_data in player and native preparer CMake.

Public771 SHA above. Detailed scope/report index lives in root
docs/stampede-exile-delivery.md. Earlier source/doc versions are archived under
registered next732/736/742/744/746/750/753/758/762/765/770 build folders.
Framework submodules were not edited; generated metadata/assets remain local.
''')
print('DOCUMENTED public771 and both-level evidence')
