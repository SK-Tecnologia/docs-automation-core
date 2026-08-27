#!/usr/bin/env node
const fs = require('fs');
const { execSync } = require('child_process');

const SEMVER_RE = /^(\d+)\.(\d+)\.(\d+)(?:-([\w.-]+))?(?:\+([\w.-]+))?$/;

function parseVersion(version) {
    const match = String(version).trim().replace(/^v/, '').match(SEMVER_RE);
    if (!match) {
        throw new Error(`Versão inválida: "${version}"`);
    }

    return {
        major: Number(match[1]),
        minor: Number(match[2]),
        patch: Number(match[3]),
        prerelease: match[4] || '',
        build: match[5] || ''
    };
}

function formatVersion(parts) {
    let version = `${parts.major}.${parts.minor}.${parts.patch}`;
    if (parts.prerelease) version += `-${parts.prerelease}`;
    if (parts.build) version += `+${parts.build}`;
    return version;
}

function bumpVersion(current, bumpType = 'patch') {
    const parts = parseVersion(current);

    if (bumpType === 'major') {
        parts.major += 1;
        parts.minor = 0;
        parts.patch = 0;
    } else if (bumpType === 'minor') {
        parts.minor += 1;
        parts.patch = 0;
    } else if (bumpType === 'patch') {
        parts.patch += 1;
    } else {
        throw new Error(`Tipo de incremento inválido: "${bumpType}". Use patch, minor ou major.`);
    }

    parts.prerelease = '';
    parts.build = '';
    return formatVersion(parts);
}

function readCurrentVersion(cwd = process.cwd()) {
    const packageJsonPath = `${cwd}/package.json`;
    if (fs.existsSync(packageJsonPath)) {
        return JSON.parse(fs.readFileSync(packageJsonPath, 'utf8')).version;
    }

    const versionFilePath = `${cwd}/VERSION`;
    if (fs.existsSync(versionFilePath)) {
        return fs.readFileSync(versionFilePath, 'utf8').trim();
    }

    try {
        const tag = execSync('git describe --tags --abbrev=0 --match "v*"', {
            cwd,
            encoding: 'utf8',
            stdio: ['ignore', 'pipe', 'ignore']
        }).trim();
        return tag.replace(/^v/, '');
    } catch {
        return '0.0.0';
    }
}

function resolveNextVersion(bumpType = 'patch', cwd = process.cwd()) {
    const current = readCurrentVersion(cwd);
    const next = bumpVersion(current, bumpType);
    return { current, next, bumpType };
}

function main() {
    const args = process.argv.slice(2);
    const shellOutput = args.includes('--shell');
    const githubOutput = args.includes('--github-output');
    const filtered = args.filter((arg) => !arg.startsWith('--'));
    const bumpType = filtered[0] || 'patch';

    if (/^\d+\.\d+\.\d+/.test(bumpType)) {
        console.error('Informe patch, minor ou major — não uma versão fixa.');
        process.exit(1);
    }

    const { current, next } = resolveNextVersion(bumpType);

    console.log(`Versão atual: ${current}`);
    console.log(`Próxima versão (+1 ${bumpType}): ${next}`);

    if (shellOutput) {
        console.log(`CURRENT=${current}`);
        console.log(`NEXT=${next}`);
    }

    if (githubOutput) {
        const outputFile = process.env.GITHUB_OUTPUT;
        if (!outputFile) {
            throw new Error('GITHUB_OUTPUT não definido.');
        }
        fs.appendFileSync(outputFile, `current=${current}\n`);
        fs.appendFileSync(outputFile, `next=${next}\n`);
        fs.appendFileSync(outputFile, `version=${next}\n`);
    }
}

if (require.main === module) {
    main();
}

module.exports = {
    bumpVersion,
    readCurrentVersion,
    resolveNextVersion
};
