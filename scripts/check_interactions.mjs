// Exercise the public interaction script without opening WhatsApp or sending data.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const script = fs.readFileSync(path.join(root, 'assets/script.js'), 'utf8');
const docListeners = new Map();
const menuListeners = new Map();
const formListeners = new Map();
const attributes = new Map();
const menuClasses = new Set();
let valid = true;
let destination = '';
let focused = false;
const navigationLinks = [];
const menuButton = {
  addEventListener: (type, fn) => menuListeners.set(type, fn),
  setAttribute: (name, value) => attributes.set(name, value),
  contains: () => false,
  focus: () => { focused = true; },
};
const navigation = {
  classList: {
    toggle: (name) => { if (menuClasses.has(name)) { menuClasses.delete(name); return false; } menuClasses.add(name); return true; },
    remove: (name) => menuClasses.delete(name),
    contains: (name) => menuClasses.has(name),
  },
  querySelectorAll: () => [{ addEventListener: (_, fn) => navigationLinks.push(fn) }],
  contains: () => false,
};
const fields = {
  service: { value: 'fayans-ustasi', selectedIndex: 0, options: [{ text: 'Fayans Ustası' }] },
  district: { value: 'odunpazari', selectedIndex: 0, options: [{ text: 'Odunpazarı' }] },
  size: { value: ' 20 m² ' },
  details: { value: 'Özel açıklama: <etiket> & ölçü' },
};
const form = {
  hidden: true,
  dataset: { whatsapp: '905433719972', source: 'https://www.yapidekorasyon.online/fayans-ustasi/eskisehir/odunpazari/' },
  elements: { namedItem: (name) => fields[name] },
  addEventListener: (name, fn) => formListeners.set(name, fn),
  reportValidity: () => valid,
};
const window = { location: { assign: (url) => { destination = url; } } };
const document = {
  body: { dataset: { pagePath: '/fayans-ustasi/eskisehir/odunpazari/', service: 'fayans-ustasi', district: 'odunpazari' } },
  addEventListener: (name, fn) => { const list = docListeners.get(name) || []; list.push(fn); docListeners.set(name, list); },
  querySelector: (selector) => selector === '[data-menu-button]' ? menuButton : navigation,
  querySelectorAll: (selector) => selector === '[data-quote-form]' ? [form] : [],
};
vm.runInNewContext(script, { document, window, Date, encodeURIComponent });
docListeners.get('DOMContentLoaded')[0]();
assert.equal(form.hidden, false);

menuListeners.get('click')();
assert.equal(attributes.get('aria-expanded'), 'true');
navigationLinks[0]();
assert.equal(attributes.get('aria-expanded'), 'false');
menuListeners.get('click')();
docListeners.get('keydown')[0]({ key: 'Escape' });
assert.equal(attributes.get('aria-expanded'), 'false');
assert.equal(focused, true);

valid = false;
formListeners.get('submit')({ preventDefault() {} });
assert.equal(destination, '');
assert.equal(window.dataLayer, undefined);
valid = true;
formListeners.get('submit')({ preventDefault() {} });
const result = new URL(destination);
assert.equal(result.origin + result.pathname, 'https://wa.me/905433719972');
const message = result.searchParams.get('text');
for (const expected of ['Hizmet: Fayans Ustası', 'İlçe: Odunpazarı', 'Yaklaşık ölçü: 20 m²', fields.details.value, 'Sayfa: ' + form.dataset.source]) assert.ok(message.includes(expected));
assert.equal(window.dataLayer.length, 1);
assert.equal(window.dataLayer[0].event, 'quote_whatsapp_open');
assert.equal(window.dataLayer[0].district_slug, 'odunpazari');
assert.ok(!JSON.stringify(window.dataLayer).includes('Özel açıklama'));
assert.ok(!JSON.stringify(window.dataLayer).includes('20 m²'));

const contact = { dataset: { contact: 'phone', placement: 'floating' } };
for (const fn of docListeners.get('click')) fn({ target: { closest: () => contact } });
assert.equal(window.dataLayer.length, 2);
assert.equal(window.dataLayer[1].event, 'contact_click');
assert.equal(window.dataLayer[1].contact_method, 'phone');
console.log('PASS: menu state, Escape, required form fields, WhatsApp number/context/encoding, single events and no free-text in measurement. No external messages sent.');
