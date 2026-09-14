export const icons = {
  paw: {
    filled: true,
    circles: [
      { cx: 12, cy: 6, r: 2 },
      { cx: 7, cy: 9.6, r: 1.6 },
      { cx: 17, cy: 9.6, r: 1.6 },
    ],
    paths: ['M9 12a2 2 0 00-2 2v1a4 4 0 004 4h2a4 4 0 004-4v-1a2 2 0 00-2-2H9z'],
  },
  'medical-cross': {
    circles: [{ cx: 12, cy: 12, r: 9 }],
    paths: ['M12 8v8M8 12h8'],
  },
  pill: {
    paths: ['M4.5 12.5l7-7a4.95 4.95 0 117 7l-7 7a4.95 4.95 0 01-7-7z', 'M8.5 8.5l7 7'],
  },
  droplet: {
    paths: ['M12 2c-4 6-7 9.5-7 13a7 7 0 0014 0c0-3.5-3-7-7-13z'],
  },
  check: {
    paths: ['M5 13l4 4L19 7'],
  },
  x: {
    paths: ['M18 6L6 18', 'M6 6l12 12'],
  },
  menu: {
    paths: ['M4 6h16', 'M4 12h16', 'M4 18h16'],
  },
  leaf: {
    paths: ['M5 21c8 0 14-6 14-14V4h-3C8 4 5 10 5 18v3z', 'M5 21c2-4 6-8 11-11'],
  },
  facebook: {
    paths: ['M14 9h3V6h-3a3 3 0 00-3 3v2H8v3h3v7h3v-7h2.5l.5-3H14V9z'],
  },
  instagram: {
    rect: { x: 3.5, y: 3.5, width: 17, height: 17, rx: 5 },
    circles: [
      { cx: 12, cy: 12, r: 3.5 },
      { cx: 16.5, cy: 7.5, r: 0.5 },
    ],
  },
  'message-circle': {
    paths: [
      'M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z',
    ],
  },
  bell: {
    paths: ['M12 3a5 5 0 00-5 5v3l-2 4h14l-2-4V8a5 5 0 00-5-5zM10 19a2 2 0 004 0'],
  },
  'chevron-down': {
    paths: ['M6 9l6 6 6-6'],
  },
  calendar: {
    paths: [
      'M8 3v3M16 3v3M4 8h16M5 6h14a1 1 0 011 1v12a1 1 0 01-1 1H5a1 1 0 01-1-1V7a1 1 0 011-1z',
    ],
  },
  'shopping-cart': {
    paths: [
      'M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.3 2.3c-.6.6-.2 1.7.7 1.7H17M17 17a2 2 0 100 4 2 2 0 000-4zM9 17a2 2 0 100 4 2 2 0 000-4z',
    ],
  },
  package: {
    paths: ['M12 2L3 7l9 5 9-5-9-5z', 'M3 7v10l9 5 9-5V7', 'M12 12v10'],
  },
  user: {
    paths: ['M12 12a4 4 0 100-8 4 4 0 000 8zM4 21a8 8 0 0116 0'],
  },
  home: {
    paths: ['M3 10l9-7 9 7', 'M5 9v10a1 1 0 001 1h3v-6h6v6h3a1 1 0 001-1V9'],
  },
  'shopping-bag': {
    paths: ['M6 8h12l-1 12H7L6 8z', 'M9 8V6a3 3 0 016 0v2'],
  },
  users: {
    circles: [
      { cx: 8, cy: 8, r: 3 },
      { cx: 16, cy: 8, r: 3 },
    ],
    paths: ['M2 20a6 6 0 0112 0', 'M12 20a6 6 0 0112 0'],
  },
  phone: {
    paths: ['M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z'],
  },
  'log-out': {
    paths: ['M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4', 'M16 17l5-5-5-5', 'M21 12H9'],
  },
  book: {
    paths: ['M4 19.5A2.5 2.5 0 016.5 17H20V4a2 2 0 00-2-2H6.5A2.5 2.5 0 004 4.5v15z'],
  },
  flag: {
    paths: ['M4 22V3', 'M4 3h14l-3 5 3 5H4z'],
  },
  stethoscope: {
    circles: [{ cx: 19.5, cy: 12.5, r: 1.8 }],
    paths: ['M6 3v5a3 3 0 006 0V3', 'M9 12v3a5 5 0 0010 0v-3.5'],
  },
  heart: {
    paths: ['M12 21s-7-4.5-9.5-9A5.5 5.5 0 0112 6a5.5 5.5 0 019.5 6c-2.5 4.5-9.5 9-9.5 9z'],
  },
  clipboard: {
    paths: [
      'M9 2h6a1 1 0 011 1v1h2a1 1 0 011 1v16a1 1 0 01-1 1H6a1 1 0 01-1-1V5a1 1 0 011-1h2V3a1 1 0 011-1z',
      'M9 12h6M9 16h6',
    ],
  },
  lightbulb: {
    paths: [
      'M9 18h6',
      'M10 22h4',
      'M12 2a7 7 0 00-4 12.7c.6.5 1 1.2 1 2.3h6c0-1.1.4-1.8 1-2.3A7 7 0 0012 2z',
    ],
  },
  shield: {
    paths: ['M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z'],
  },
  clock: {
    circles: [{ cx: 12, cy: 12, r: 9 }],
    paths: ['M12 7v5l4 2'],
  },
  'map-pin': {
    circles: [{ cx: 12, cy: 9, r: 2.5 }],
    paths: ['M12 21s7-7.5 7-12a7 7 0 10-14 0c0 4.5 7 12 7 12z'],
  },
  bug: {
    circles: [
      { cx: 12, cy: 14, r: 5 },
      { cx: 12, cy: 7, r: 2 },
    ],
    paths: ['M7 14H3M17 14h4M8 18l-3 3M16 18l3 3M8 10l-3-3M16 10l3-3'],
  },
  flask: {
    paths: ['M9 2v6l-5 10a2 2 0 002 3h12a2 2 0 002-3L15 8V2', 'M9 2h6'],
  },
  search: {
    circles: [{ cx: 10, cy: 10, r: 8 }],
    paths: ['M21 21l-4.35-4.35'],
  },
  mail: {
    paths: ['M4 4h16v16H4V4z', 'M4 4l8 8 8-8'],
  },
  'alert-triangle': {
    paths: [
      'M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z',
      'M12 9v4',
      'M12 17h.01',
    ],
  },
  refresh: {
    paths: [
      'M4 4v6h6',
      'M20 20v-6h-6',
      'M4.5 15a8 8 0 0013.5 3.5L20 20',
      'M20 9a8 8 0 00-13.5-3.5L4 9',
    ],
  },
  archive: {
    paths: ['M3 8h18v3H3V8z', 'M4 11v9a1 1 0 001 1h14a1 1 0 001-1v-9', 'M10 15h4'],
  },
  headset: {
    circles: [
      { cx: 4.5, cy: 16, r: 2.2 },
      { cx: 19.5, cy: 16, r: 2.2 },
    ],
    paths: ['M4 14v-2a8 8 0 0116 0v2'],
  },
  frown: {
    circles: [{ cx: 12, cy: 12, r: 9 }],
    paths: ['M8 15s1.5-2 4-2 4 2 4 2', 'M9 9h.01M15 9h.01'],
  },
  'file-text': {
    paths: [
      'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z',
      'M14 2v6h6',
      'M8 13h8M8 17h8M8 9h2',
    ],
  },
  edit: {
    paths: ['M12 20h9', 'M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4 12.5-12.5z'],
  },
  send: {
    paths: ['M22 2L11 13', 'M22 2l-7 20-4-9-9-4 20-7z'],
  },
  cloud: {
    paths: ['M17.5 19a4.5 4.5 0 000-9 6 6 0 00-11.4-1.5A4.5 4.5 0 006.5 19h11z'],
  },
  plus: {
    paths: ['M12 5v14', 'M5 12h14'],
  },
  'arrow-left': {
    paths: ['M19 12H5', 'M12 19l-7-7 7-7'],
  },
  camera: {
    circles: [{ cx: 12, cy: 13, r: 3.5 }],
    paths: ['M4 8h3l2-3h6l2 3h3a1 1 0 011 1v10a1 1 0 01-1 1H4a1 1 0 01-1-1V9a1 1 0 011-1z'],
  },
  'gender-male': {
    circles: [{ cx: 10, cy: 14, r: 5 }],
    paths: ['M14 10l5-5', 'M14 5h5v5'],
  },
  'gender-female': {
    circles: [{ cx: 12, cy: 9, r: 5 }],
    paths: ['M12 14v7', 'M9 18h6'],
  },
  'help-circle': {
    circles: [{ cx: 12, cy: 12, r: 9 }],
    paths: ['M9.5 9a2.5 2.5 0 115 .5c0 1.8-2.5 1.8-2.5 3.7', 'M12 17h.01'],
  },
  'chevron-left': {
    paths: ['M15 18l-6-6 6-6'],
  },
  'chevron-right': {
    paths: ['M9 18l6-6-6-6'],
  },
  eye: {
    circles: [{ cx: 12, cy: 12, r: 3 }],
    paths: ['M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z'],
  },
  info: {
    circles: [{ cx: 12, cy: 12, r: 9 }],
    paths: ['M12 8h.01', 'M11 11.5h1.2v5'],
  },
  tag: {
    circles: [{ cx: 8, cy: 8, r: 1.2 }],
    paths: ['M12.5 3H5a2 2 0 00-2 2v7.5a2 2 0 00.6 1.4l8.5 8.5a2 2 0 002.8 0l6-6a2 2 0 000-2.8l-8.5-8.5a2 2 0 00-1.4-.6z'],
  },
  truck: {
    circles: [
      { cx: 6.5, cy: 18, r: 1.8 },
      { cx: 17, cy: 18, r: 1.8 },
    ],
    paths: ['M3 6h11v9H3z', 'M14 10h4l3 3.5V15h-7z', 'M8.3 18h6.4'],
  },
  'arrow-back-up': {
    paths: ['M5 10h9a5 5 0 010 10h-3', 'M9 6L5 10l4 4'],
  },
  'file-invoice': {
    paths: [
      'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z',
      'M14 2v6h6',
      'M8 12h8M8 15.5h8M8 19h4',
    ],
  },
  cash: {
    circles: [{ cx: 12, cy: 12, r: 2.5 }],
    paths: ['M2.5 6h19v12h-19z', 'M6 6v12M18 6v12'],
  },
  'chart-bar': {
    paths: ['M4 20V10M10 20V4M16 20v-7M22 20H2'],
  },
  'user-check': {
    circles: [{ cx: 9, cy: 8, r: 3.5 }],
    paths: ['M2.5 20a6.5 6.5 0 0113 0', 'M16.5 12l2 2 3.5-3.5'],
  },
  'shield-check': {
    paths: ['M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z', 'M9 12l2 2 4-4'],
  },
  download: {
    paths: ['M12 3v10', 'M7 9l5 5 5-5', 'M4 19h16'],
  },
}
