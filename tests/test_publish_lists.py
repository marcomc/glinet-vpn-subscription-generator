import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class PublicationTests(unittest.TestCase):
    def test_public_checkout_does_not_require_deploy_key(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/update-lists.yml').read_text())
        steps = workflow['jobs']['generate']['steps']
        checkout = next(step for step in steps
                        if step.get('with', {}).get('repository') ==
                        'marcomc/glinet-vpn-subscription-lists')
        self.assertNotIn('ssh-key', checkout['with'])
        self.assertFalse(checkout['with']['persist-credentials'])
        self.assertEqual(checkout['with']['ref'], 'main')
        secret_steps = [step for step in steps if 'secrets.LISTS_DEPLOY_KEY' in str(step)]
        self.assertEqual(len(secret_steps), 1)
        self.assertEqual(secret_steps[0]['run'], 'bash ../generator/scripts/publish_lists.sh')

    def publish(self, changed, key='', fail_push=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / 'lists'
            repository.mkdir()
            subprocess.run(['git', 'init', '-q', str(repository)], check=True)
            subprocess.run(['git', '-C', str(repository), 'config', 'user.name', 'Test'], check=True)
            subprocess.run(['git', '-C', str(repository), 'config', 'user.email', 'test@example.com'], check=True)
            (repository / 'output').mkdir()
            (repository / 'reports').mkdir()
            (repository / 'README.md').write_text('Catalog\n')
            (repository / 'output/list.txt').write_text('example.com\n')
            (repository / 'output/obsolete.txt').write_text('obsolete.example.com\n')
            (repository / 'reports/coverage.json').write_text('{}\n')
            subprocess.run(['git', '-C', str(repository), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(repository), 'commit', '-qm', 'Initial'], check=True)
            if changed:
                (repository / 'README.md').write_text('Updated catalog\n')
                (repository / 'output/list.txt').write_text('example.org\n')
                (repository / 'output/obsolete.txt').unlink()
                (repository / 'reports/coverage.json').write_text('{"updated": true}\n')
                (repository / 'unrelated.txt').write_text('Must remain unpublished\n')
            remote = root / 'remote.git'
            subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
            # Intercept only the SSH transport; staging and commits use real Git.
            transport = root / 'ssh'
            transport.write_text('''#!/usr/bin/env python3
import os
import stat
import sys
from pathlib import Path
args = sys.argv[1:]
key = Path(args[args.index('-i') + 1])
assert key.read_text() == 'test-private-key\\n'
assert stat.S_IMODE(key.stat().st_mode) == 0o600
assert stat.S_IMODE(key.parent.stat().st_mode) == 0o700
assert 'LISTS_DEPLOY_KEY' not in os.environ
assert 'StrictHostKeyChecking=yes' in args
assert 'IdentitiesOnly=yes' in args
assert 'BatchMode=yes' in args
assert 'github.com ssh-ed25519 ' in (key.parent / 'known_hosts').read_text()
Path(os.environ['SSH_MARKER']).write_text(str(key.parent))
if os.environ['FAIL_PUSH'] == '1':
    sys.exit(1)
if '-G' in args:
    sys.exit(0)
assert args[-2:] == ['git@github.com', \"git-receive-pack 'marcomc/glinet-vpn-subscription-lists.git'\"]
os.execvp('git-receive-pack', ['git-receive-pack', os.environ['TEST_REMOTE']])
''')
            transport.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            marker = root / 'ssh-used'
            environment = dict(os.environ, PATH=f'{root}{os.pathsep}{os.environ["PATH"]}',
                               LISTS_DEPLOY_KEY=key, SSH_MARKER=str(marker),
                               FAIL_PUSH=str(int(fail_push)), TMPDIR=str(root), TEST_REMOTE=str(remote))
            result = subprocess.run(['bash', str(ROOT / 'scripts/publish_lists.sh')],
                                    cwd=repository, env=environment, capture_output=True, text=True)
            if marker.exists():
                self.assertFalse(Path(marker.read_text()).exists(), 'Temporary key must be removed')
            if changed and key and not fail_push:
                expected = {
                    'README.md': 'Updated catalog\n',
                    'output/list.txt': 'example.org\n',
                    'reports/coverage.json': '{"updated": true}\n',
                }
                published_paths = subprocess.check_output(
                    ['git', '--git-dir', str(remote), 'ls-tree', '-r', '--name-only', 'main'],
                    text=True,
                ).splitlines()
                self.assertEqual(set(published_paths), set(expected))
                for file_path, content in expected.items():
                    published = subprocess.check_output(
                        ['git', '--git-dir', str(remote), 'show', f'main:{file_path}'], text=True,
                    )
                    self.assertEqual(published, content)
            self.assertNotIn('test-private-key', result.stdout + result.stderr)
            commits = subprocess.check_output(['git', '-C', str(repository), 'rev-list', '--count', 'HEAD'], text=True)
            return result, marker.exists(), int(commits)

    def test_no_changes_succeeds_without_key_or_ssh(self):
        result, used_ssh, commits = self.publish(changed=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(used_ssh)
        self.assertEqual(commits, 1)

    def test_changes_require_key_before_commit(self):
        result, used_ssh, commits = self.publish(changed=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('LISTS_DEPLOY_KEY is required', result.stderr)
        self.assertFalse(used_ssh)
        self.assertEqual(commits, 1)

    def test_changed_lists_are_published_and_key_is_removed(self):
        result, used_ssh, commits = self.publish(changed=True, key='test-private-key')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(used_ssh)
        self.assertEqual(commits, 2)

    def test_push_failure_is_reported_and_key_is_removed(self):
        result, used_ssh, commits = self.publish(changed=True, key='test-private-key', fail_push=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(used_ssh, result.stderr)
        self.assertEqual(commits, 2)


if __name__ == '__main__':
    unittest.main()
