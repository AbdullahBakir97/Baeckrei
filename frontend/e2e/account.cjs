// The accounts the e2e server creates (throwaway database only).
module.exports = {
  email: 'e2e@example.com',
  password: ['Rye', 'Crust', 'Oven', '2026'].join('-'),
  admin: {
    email: 'owner@example.com',
    password: ['Sour', 'Dough', 'Owner', '2026'].join('-')
  }
}
