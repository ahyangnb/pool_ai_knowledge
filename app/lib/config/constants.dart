class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://192.168.155.23:8000',
  );

  static const int homePostsLimit = 6;
  static const int postsPageSize = 12;
  static const int chatPostOptionsLimit = 100;
}
