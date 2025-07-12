import typescriptEslint from "@typescript-eslint/eslint-plugin";
import robloxTs from "eslint-plugin-roblox-ts";
import prettier from "eslint-plugin-prettier";
import tsParser from "@typescript-eslint/parser";
import path from "node:path";
import { fileURLToPath } from "node:url";
import eslint from '@eslint/js';
import { FlatCompat } from "@eslint/eslintrc";
import tseslint from 'typescript-eslint';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: eslint.configs.recommended,
    allConfig: eslint.configs.all
});

export default tseslint.config(
    {
        files: ["**/*.ts", "**/*.tsx"],
        ignores: ["**/*.js", "**/*.cjs", "**/*.mjs", "**/out/**"],

        plugins: {
            "@typescript-eslint": typescriptEslint,
            "roblox-ts": robloxTs,
            "prettier": prettier,
        },
        extends: [
            eslint.configs.recommended,
            tseslint.configs.strictTypeChecked,
            tseslint.configs.stylisticTypeChecked,
            compat.extends("plugin:prettier/recommended"),
            //compat.extends("plugin:roblox-ts/recommended"),
        ],
        languageOptions: {
            parser: tsParser,
            ecmaVersion: 2018,
            sourceType: "module",

            parserOptions: {
                jsx: true,
                useJSXTextNode: true,
                tsconfigRootDir: ".",
                project: "tsconfig.json"
            }
        },

        rules: {
            "prettier/prettier": "warn",
            "@typescript-eslint/restrict-template-expressions": "off",
            "@typescript-eslint/no-explicit-any": "off",
            "@typescript-eslint/no-non-null-assertion": "off",
            "@typescript-eslint/no-unused-vars": "warn",
            "@typescript-eslint/no-namespace": "off",
            "@typescript-eslint/no-require-imports": "off",
            "prefer-const": "off",
            "semi": "warn",
            "no-empty": "off",
        },
    }
);