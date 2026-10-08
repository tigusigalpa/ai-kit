# Moodle: apply only to a confirmed Moodle project

- Check the Moodle version, plugin type, `version.php` structure, components, and the project's current Moodle coding guidelines. For a plugin task, use a supported extension rather than editing the core when one is available.
- Use Moodle APIs for data access, permissions, forms, events, language, and output. Check capabilities, context, sesskey, and output protection according to the actual use case.
- For schema changes, check `db/install.xml` and the existing `db/upgrade.php`; provide a correct upgrade step for existing installations as well as fresh installations. Check the plugin version and upgrade path.
- Verify compatibility with supported Moodle/PHP versions. Run relevant PHPUnit and Behat checks using actual configured project commands.
- Avoid unnecessary personal data or course content in diagnostic messages. Account for roles, contexts, and privacy during review.
