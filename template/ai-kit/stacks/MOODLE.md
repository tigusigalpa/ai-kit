# Moodle installation or plugin

Confirm Moodle/PHP versions, plugin type, component, version.php, upgrade history, and actual PHPUnit/Behat commands.
- Extend supported plugin APIs rather than editing core. Use Moodle data, forms, events, output, and language APIs.
- Pair the correct context with require_capability/checks; protect state-changing requests with sesskey and avoid trusting client roles.
- Use get_string and component lang files; escape output according to the renderer/data type. Keep authored project strings English unless explicitly requested otherwise.
- For schema changes update install.xml, add version-gated upgrade.php steps/savepoints, and bump the plugin version appropriately. Test fresh and existing installations; batch large backfills and bound locks/reruns.
- Audit personal data storage/export/deletion. Implement the applicable Privacy API provider; use a null provider only after establishing that no personal data is stored.
- Use Moodle cache APIs with defined keys/invalidation; do not cache capabilities or personal content across contexts incorrectly.
- Test role/context/capability combinations, migration paths, and privacy behavior. Avoid course/user data in diagnostics.

Match the installed branch of [Privacy API](https://moodledev.io/docs/5.1/apis/subsystems/privacy) and [plugin upgrades](https://moodledev.io/docs/5.1/guides/upgrade).
