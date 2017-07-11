'use strict';
// Object to store message names
const MSG = Object.freeze({
    ERASE_OBJECT: 'MSG_ERASE_OBJECT',
    GET_URL: 'MSG_GET_URL',
    PREDICT_CLASS: 'MSG_PREDICT_CLASS',
    TOGGLE_STATE: 'MSG_TOGGLE_STATE',
    GET_STATE: 'MSG_GET_STATE',
    DOM_LOADED: 'MSG_DOM_LOADED'
});
const MSG_KEYS = Object.freeze({
    NAME: 'MSG_NAME',
    CURRENT_URL: 'MSG_CURRENT_URL',
    ERASE_OBJECT: 'MSG_ERASE_OBJECT'
});
const RESPONSE_KEYS = Object.freeze({
    PREDICTED_CLASSES: 'RESPONSE_PREDICTED_CLASSES',
    CURRENT_STATE: 'RESPONSE_CURRENT_STATE',
    URL: 'RESPONSE_URL',
    SUCCESS: 'RESPONSE_SUCCESS'
});
const ERASE_KEYS = Object.freeze({
    FILTER_TERMS: 'ERASE_FILTER_TERMS',
    CLASS_NAMES: 'ERASE_CLASS_NAMES'
});
const ELEMENTS = Object.freeze({
    INPUT_FILTER_TERM: document.getElementById('inputFilterTerm'),
    UNORDERED_LIST_FILTER_TERMS: document.getElementById('listFilterTerms'),
    INPUT_CONTAINER_CLASS_NAME: document.getElementById('inputClassName'),
    UNORDERED_LIST_CLASS_NAMES: document.getElementById('listClassNames'),
    INPUT_URL_KEY: document.getElementById('inputURLKey'),
    BUTTON_ERASE: document.getElementById('buttonErase'),
    BUTTON_STORE: document.getElementById('buttonStoreData'),
    BUTTON_RETRIEVE: document.getElementById('buttonRetrieveData'),
    BUTTON_PREDICT: document.getElementById('buttonPredictClass'),
    TOGGLE_STATE: document.getElementById('toggleContinuous'),
    TOGGLE_STATE_LABEL : document.getElementById('toggleContinuousLabel'),
    TOOLTIP: document.getElementById('tooltip')
});

const KEY_CODES = Object.freeze({
    ENTER: 13,
    TAB: 9
});

const EVENTS = Object.freeze({
    CLICK: 'click',
    KEY_DOWN: 'keydown',
    INPUT: 'input',
    CHANGE: 'change',
    DOCUMENT_LOADED: 'DOMContentLoaded'
});

const STATE = Object.freeze({
    OFF: false,
    ON: true
});

const TIMERS = Object.freeze({
    ERASE_DIVS: 2 * 1000,
    TOOLTIP: 3000
});

const ACTIVE_TAB_QUERY = Object.freeze({
    active: true,
    currentWindow: true
});

const ELEMENT_INFO = Object.freeze({
    COUNT: 'COUNT',
    DEPTH: 'DEPTH',
    AVG_TEXT_COUNT: 'AVERAGE_TEXT_COUNT',
    CLASS_NAME: 'CLASS_NAME',
    GENERATED_ID: 'GENERATED_ID'
});

const THRESHOLDS = Object.freeze({
    COUNT: 5,
    AVG_TEXT_COUNT: 50,
    TOP_N: 3
});

const BULMA_CLASSES = Object.freeze({
    IS_LOADING: 'is-loading',
    IS_DANGER: 'is-danger',
    IS_HIDDEN: 'is-hidden'
});

const STRING = Object.freeze({
    TOGGLE_STATE_ON: 'Running continuously! (Click to turn off)',
    TOGGLE_STATE_OFF: 'Not running continuously',
    NO_PREDICTIONS_FOUND: 'Could not predict any class names for containers',
    KEY_NEEDED_FOR_STORAGE: 'You need to enter a key to store settings',
    KEY_NEEDED_FOR_RETRIEVAL: 'You need to enter a key to retrieve past settings',
    KEY_NOT_FOUND: 'No past settings found for the entered key'
});