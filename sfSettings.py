# sfSettings: at the moment a simple dict with some settings
settings={
    'MIN_NEARCLICK_DISTANCE': 16,
    'CORNER_DRAG_HANDLE_SIZE': 4,
    'SIDE_DRAG_HANDLE_SIZE': 6,
    'MOUSE_TIMING': {
        'LONG_CLICK_TIME_MS': 500 
    },
    'WINDOW_SIZE': {
        'WIDTH': 700,
        'HEIGHT': 550,
    },
    'ZOOM': {
        'FACTOR_X': 4,
        'FACTOR_Y': 4,
        'IMAGE_WIDTH': 60,
        'IMAGE_HEIGHT': 60,
    },
    'COLOR': {
        'EDITING': 'red',
        'INERT': 'green',
        'SELECTABLE': 'orange',
        'LABELING': 'blue',
        'LABELING_BACKGROUND': '#C0C0FF',
    },
    'LABELTEXT': {
        'FONTFAMILY': 'Helvetica',
        'FONTSIZE': 12,
        'FONTWEIGHT': 'bold',
    },
    'RECTANGLE': {
        'WIDTH': 3,
        'BOTTOMWIDTH': 1,
        'BOTTOMFRACTION': 0.86,
    },
    'DEBUG': True,
    'DEBUG_BUTTON': False,
    'MAX_DIRNAME_LENGTH': 32,
    'TARGET_SUBDIRECTORY': 'sfClips',
    'VERSION': '1.0',
    'AUTORECTANGLES': {             # Auto-recognition of clip rectangles
        'ACTIVE': True,
        'EROSIONITERATIONS': 15,
        'DILATIONITERATIONS': 12,
        'MINREGIONSIZE': None,      # None (auto) or a fraction <=1 of total pixels
        'WHITETHRESHOLD': None,     # None (auto) or a 0-256 greyscale white threshold
        'SHRINKFACTOR': 8,          # Shrink factor: high=fast but not too accurate
    },
}
