/* LDC-B shared French search normalizer.
   Single runtime/build authority: browser exposes window.LDCSearch; Node uses module.exports. */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.LDCSearch = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';
  const VERSION = 'ldc-search-normalizer-v1';
  function normalise(input) {
    return String(input == null ? '' : input).toLowerCase()
      .replace(/[éèêë]/g,'e').replace(/[àâ]/g,'a').replace(/[îï]/g,'i')
      .replace(/[ôö]/g,'o').replace(/[ùûü]/g,'u').replace(/ç/g,'c')
      .replace(/œ/g,'oe').replace(/æ/g,'ae')
      .replace(/[\u00A0\u202F]/g,' ')
      .replace(/[‘’‚‛]/g,' ').replace(/[-–—]/g,' ')
      .replace(/[^A-Za-z0-9\s]/g,' ')
      .replace(/\s+/g,' ').trim();
  }
  function terms(input, minLength) {
    const min = Number.isInteger(minLength) ? minLength : 3;
    return normalise(input).split(' ').filter(Boolean).filter(t => t.length >= min);
  }
  return Object.freeze({ VERSION, normalise, terms });
});
