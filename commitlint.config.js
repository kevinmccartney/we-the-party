const configConventional = require('@commitlint/config-conventional');

const config = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      // extending the commit types in config-conventional
      [...configConventional.rules['type-enum'][2], 'release'],
    ],
  },
  prompt: {
    questions: {
      type: {
        enum: {
          ...configConventional.prompt.questions.enum,
          release: {
            description: 'A new release',
            title: 'Release',
            emoji: '📦',
          },
        },
      },
    },
  },
};

module.exports = config;
