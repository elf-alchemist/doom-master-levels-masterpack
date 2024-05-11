#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Guilherme M. Miranda <alchemist.software@proton.me>
#
# Description:
#     Masterpack base builder, a utility for creating the base.wad file needed for building masterpack.wad

from os import listdir
from hashlib import sha256

from omg.wad import WAD
from omg.mapedit import MapEditor

logfile = None
LOG_FILE = 'base.log'

BUFFER_SIZE = 16384

DIR_SOURCE = 'base/'

ALPHA = 'alpha.wad'
BASE = 'beta.wad'

SOURCE_WADS = [
    # Inferno
    'DANTE25.WAD',
    'ACHRON22.WAD',
    'UDTWiD.wad',
    # Titan
    'MINES.WAD',
    'anomaly.wad',
    'FARSIDE.WAD',
    'TROUBLE.WAD',
]

SOURCE_SHA256SUM = {
    # Alpha
    'alpha.wad': '9b625634ab84381cba8136dcc3625d08b24375cb226806f01a7ffe6225bcb3c7',
    # Inferno
    'DANTE25.WAD': '8ac0ce535c75027f46a8909ad6fa7c173ba1457a76167a05ac2213d5606cf902',
    'ACHRON22.WAD': '9c285f5b14b5a26a5e46e0c5566a1fbfc94a170a9d0d6c2dee19069b3e4d5423',
    'UDTWiD.wad': '523108f0341da424fc390c2a43cb3a9d418f0137298e85b19d12272da4021ec7',
    # Titan
    'MINES.WAD': '4156ed584a667f3d97cd4e3795e0cafa7194404855d9c88826e6e417da9e5d5d',
    'anomaly.wad': 'e0d3efc52add92974cf989c34ce93dbb35149041a1192a2ea169e24922490dad',
    'FARSIDE.WAD': '55e40715b49c201ea035eef00b5ece40243ca217a56b20c1fb7625c7103ac277',
    'TROUBLE.WAD': '8f89694bdaeb10709acea88423929bf4ea75cfc8f6d406565151076ccbc365f5',
}

PATCH_TRIPLETS = [
    # patch X, in wad Y, as Z
    ['SKY4', 'UDTWiD.wad', 'SKY4'],
    ['RSKY6_1', 'MINES.WAD', 'STARS'],
    ['RSKY6_2', 'MINES.WAD', 'STARS1'],
    ['RSKY6_3', 'MINES.WAD', 'STARSAT'],
    # Inferno
    ['DRSLEEP', 'UDTWiD.wad', 'DRSLEEP'],
    # Titan
    ['ASHWALL', 'MINES.WAD', 'W104_1'],
    ['WATER', 'MINES.WAD', 'TWF'],
    ['REDWALL1', 'MINES.WAD', 'W15_4'],
    ['REDWALL2', 'MINES.WAD', 'W15_5'],
    ['BLACK', 'anomaly.wad', 'BLACK'],
    ['FIRELV', 'anomaly.wad', 'FIRELV'],
    ['ANOMALY1', 'anomaly.wad', 'S_DOOM09'],
    ['ANOMALY2', 'anomaly.wad', 'S_DOOM10'],
    ['ANOMALY3', 'anomaly.wad', 'S_DOOM11'],
    ['ANOMALY4', 'anomaly.wad', 'S_DOOM12'],
    ['ANOMALY5', 'anomaly.wad', 'S_DOOM13'],
    ['ANOMALY6', 'anomaly.wad', 'S_DOOM14'],
    ['ANOMALY7', 'anomaly.wad', 'S_DOOM15'],
    ['ANOMALY8', 'anomaly.wad', 'S_DOOM16'],
    ['SAVED', 'TROUBLE.WAD', 'SAVED'],
    ['TROUBLE1', 'TROUBLE.WAD', 'TROU00'],
    ['TROUBLE2', 'TROUBLE.WAD', 'TROU01'],
    ['TROUBLE3', 'TROUBLE.WAD', 'TROU06'],
    ['TROUBLE4', 'TROUBLE.WAD', 'TROU07'],
    ['TROUBLE5', 'TROUBLE.WAD', 'TROU13'],
]

MAP_TRIPLETS = [
    # Inferno
    ['MAP01', 'DANTE25.WAD', 'MAP02'],
    ['MAP02', 'ACHRON22.WAD', 'MAP03'],
    ['MAP09', 'UDTWiD.wad', 'E4M8'],
    # Titan
    ['MAP10', 'MINES.WAD', 'MAP01'],
    ['MAP11', 'anomaly.wad', 'MAP01'],
    ['MAP12', 'FARSIDE.WAD', 'MAP01'],
    ['MAP15', 'TROUBLE.WAD', 'MAP01'],
]

BASE_PATCHES = [
    # UDTWiD
    'SKY4',
    # Master Levels
    # 'RSKY4',        # light stars
    'RSKY5',        # medium stars
    'RSKY6_1',      # heavy stars
    'RSKY6_2',      # heavy stars, nebula
    'RSKY6_3',      # heavy stars, saturn
    # UDTWiD
    'DRSLEEP',
    # MINES.WAD
    'ASHWALL',
    'WATER',
    'REDWALL1',
    'REDWALL2',
    # anomaly.wad
    'BLACK',
    'FIRELV',
    'ANOMALY1',
    'ANOMALY2',
    'ANOMALY3',
    'ANOMALY4',
    'ANOMALY5',
    'ANOMALY6',
    'ANOMALY7',
    'ANOMALY8',
    # TROUBLE.WAD
    'SAVED',
    'TROUBLE1',
    'TROUBLE2',
    'TROUBLE3',
    'TROUBLE4',
    'TROUBLE5',
]

BASE_MAPS = [
    # Inferno
    'MAP01',
    'MAP02',
    'MAP09',
    # Titan
    'MAP10',
    'MAP11',
    'MAP12',
    'MAP15',
]


#
# Utils
#


def log(line: str) -> None:
    global logfile

    if not logfile:
        logfile = open(LOG_FILE, 'w')

    print(line)
    logfile.write(line + '\n')


def get_wad_filename(wad_name: str) -> str | None:
    for filename in listdir(DIR_SOURCE):
        if wad_name.lower() == filename.lower():
            return DIR_SOURCE + filename

    return None


#
# Check WAD data
#


def get_wad_pre_hash(wad_name: str) -> str | None:
    if wad_name not in SOURCE_SHA256SUM:
        return None

    return SOURCE_SHA256SUM[wad_name]


def get_wad_hash(wad_path: str) -> str | None:
    sha256hash = sha256()

    file_handler = open(wad_path, 'rb')

    while True:
        data = file_handler.read(BUFFER_SIZE)
        if not data:
            break
        sha256hash.update(data)

    return sha256hash.hexdigest()


def check_wads(found_wads: list[str]):
    for wad in SOURCE_WADS:
        if get_wad_filename(wad) == None:
            log(f'  {wad.upper()} is missing.')

        if get_wad_hash(DIR_SOURCE + wad) != get_wad_pre_hash(wad):
            log(f'  {wad.upper()} checksum does not match. Continuing with caution. If you see no other errors or warnings, ignore this one.')

        found_wads.append(wad)


#
# Actual lump-to-wad extraction
#


def massive_simple_sidedef_switch(map: MapEditor, initial_tx: str, desired_tx: str) -> None:
    for sidedef in map.sidedefs:
        if sidedef.tx_up == initial_tx:
            sidedef.tx_up = desired_tx
        if sidedef.tx_mid == initial_tx:
            sidedef.tx_mid = desired_tx
        if sidedef.tx_low == initial_tx:
            sidedef.tx_low = desired_tx


def base_build() -> None:
    base = WAD()
    alpha = WAD('alpha.wad')

    # if get_wad_hash(ALPHA) != get_wad_pre_hash(ALPHA):
    # log('  Error: alpha.wad failed the checksum, something terrible happened. Try again.')
    # log('Build failed.')
    # exit(2)

    log('  Extracting patches...')
    # Canto 2 has it's single patch outside the P_* markers
    achron22 = WAD(DIR_SOURCE + 'ACHRON22.WAD')
    sky = achron22.data['RSKY1']
    alpha.patches['RSKY5'] = sky
    # thankfully all others are marked properly
    for triple in PATCH_TRIPLETS:
        wad = WAD(DIR_SOURCE + triple[1])
        patch = wad.patches[triple[2]]
        alpha.patches[triple[0]] = patch

    log('  Extracting maps...')
    for triple in MAP_TRIPLETS:
        wad = WAD(DIR_SOURCE + triple[1])
        map = wad.maps[triple[2]]
        alpha.maps[triple[0]] = map

    log('    Fixing MAP10...')
    map10 = MapEditor(alpha.maps['MAP10'])
    massive_simple_sidedef_switch(map10, 'DBRAIN1', 'WATER')
    massive_simple_sidedef_switch(map10, 'SW1COMP', 'TT1COMP')
    massive_simple_sidedef_switch(map10, 'SW2COMP', 'TT2COMP')
    massive_simple_sidedef_switch(map10, 'SW1STON1', 'TT1STON1')
    massive_simple_sidedef_switch(map10, 'SW2STON1', 'TT2STON1')
    alpha.maps['MAP10'] = map10.to_lumps()

    log('    Fixing MAP11...')
    map11 = MapEditor(alpha.maps['MAP11'])
    massive_simple_sidedef_switch(map11, 'SW1STON2', 'TT1STON2')
    massive_simple_sidedef_switch(map11, 'SW2STON2', 'TT2STON2')
    alpha.maps['MAP11'] = map11.to_lumps()

    log('    Fixing MAP12...')
    map12 = MapEditor(alpha.maps['MAP12'])
    massive_simple_sidedef_switch(map12, 'SW1BRIK', 'TT1BRIK')
    massive_simple_sidedef_switch(map12, 'SW2BRIK', 'TT2BRIK')
    massive_simple_sidedef_switch(map12, 'SW1STON3', 'TT1STON3')
    massive_simple_sidedef_switch(map12, 'SW2STON3', 'TT2STON3')
    massive_simple_sidedef_switch(map12, 'SW1STON4', 'TT1STON4')
    massive_simple_sidedef_switch(map12, 'SW2STON4', 'TT2STON4')
    alpha.maps['MAP12'] = map12.to_lumps()

    log('    Fixing MAP15...')
    map15 = MapEditor(alpha.maps['MAP15'])
    massive_simple_sidedef_switch(map15, 'SW1VINE', 'TT1VINE')
    massive_simple_sidedef_switch(map15, 'SW2VINE', 'TT2VINE')
    massive_simple_sidedef_switch(map15, 'SW1PIPE', 'TT1PIPE')
    massive_simple_sidedef_switch(map15, 'SW2PIPE', 'TT2PIPE')
    massive_simple_sidedef_switch(map15, 'SW1STON5', 'TT1STON5')
    massive_simple_sidedef_switch(map15, 'SW2STON5', 'TT2STON5')
    massive_simple_sidedef_switch(map15, 'SW1STON6', 'TT1STON6')
    massive_simple_sidedef_switch(map15, 'SW2STON6', 'TT2STON6')
    massive_simple_sidedef_switch(map15, 'SW1STON7', 'TT1STON7')
    massive_simple_sidedef_switch(map15, 'SW2STON7', 'TT2STON7')
    massive_simple_sidedef_switch(map15, 'PIC00', 'PORTAL1')
    massive_simple_sidedef_switch(map15, 'PIC01', 'PORTAL2')
    massive_simple_sidedef_switch(map15, 'PIC06', 'PORTAL3')
    massive_simple_sidedef_switch(map15, 'PIC07', 'PORTAL4')
    massive_simple_sidedef_switch(map15, 'PIC13', 'PORTAL5')
    alpha.maps['MAP15'] = map15.to_lumps()

    log('  Transferring lumps...')
    base.data += alpha.data
    base.music += alpha.music
    base.txdefs += alpha.txdefs
    base.patches += alpha.patches
    base.graphics += alpha.graphics
    log('    Ordering lumps...')
    for patch in BASE_PATCHES:
        base.patches[patch] = alpha.patches[patch]
    for map in BASE_MAPS:
        base.maps[map] = alpha.maps[map]

    log('  Creating base.wad...')
    base.to_file(BASE)

    # if get_wad_hash(BASE) != get_wad_pre_hash(BASE):
    #    log('  Warn: base.wad failed the checksum, you can _maybe_ build masterpack.wad.')


def main() -> None:
    log('Checking wads.')
    found_wads: list[str] = []
    check_wads(found_wads)

    if sorted(found_wads) != sorted(SOURCE_WADS):
        log('Error: Did not find all base wads. Check base.log for more details.')
        log('Build failed. Exiting...')
        exit(1)
    log(' Found all base WADs!')

    log('Starting to build WAD.')
    base_build()

    log('Build successful.')
    exit(0)


if __name__ == '__main__':
    main()
