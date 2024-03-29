module.exports = {
  env: {
    browser: true,
    es2021: true
  },
  extends: ['plugin:react/recommended', 'standard'],
  settings: {
    react: {
      version: 'detect'
    }
  },
  overrides: [],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  plugins: ['react'],
  rules: {
    'space-before-function-paren': 'off',
    'react/prop-types': 'off',
    semi: 'off',
    'multiline-ternary': 'off',
    'react/no-children-prop': 'off',
    indent: 'off',
    'no-unused-vars': 'off'
  }
};
