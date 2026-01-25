class Post {
  final String? id;
  final String title;
  final String content;
  final String? summary;
  final List<String>? tags;
  final bool isPublished;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  Post({
    this.id,
    required this.title,
    required this.content,
    this.summary,
    this.tags,
    this.isPublished = false,
    this.createdAt,
    this.updatedAt,
  });

  factory Post.fromJson(Map<String, dynamic> json) {
    return Post(
      id: json['id']?.toString(),
      title: json['title'] ?? '',
      content: json['content'] ?? '',
      summary: json['summary'],
      tags: json['tags'] != null ? List<String>.from(json['tags']) : null,
      isPublished: json['is_active'] ?? false,
      createdAt:
          json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt:
          json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }
}

class PostCreate {
  final String title;
  final String content;
  final String? summary;
  final List<String>? tags;
  final bool isPublished;

  PostCreate({
    required this.title,
    required this.content,
    this.summary,
    this.tags,
    this.isPublished = false,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'title': title,
      'content': content,
      'is_published': isPublished,
    };
    if (summary != null) map['summary'] = summary;
    if (tags != null) map['tags'] = tags;
    return map;
  }
}

class PostUpdate {
  final String? title;
  final String? content;
  final String? summary;
  final List<String>? tags;
  final bool? isPublished;

  PostUpdate({
    this.title,
    this.content,
    this.summary,
    this.tags,
    this.isPublished,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (title != null) map['title'] = title;
    if (content != null) map['content'] = content;
    if (summary != null) map['summary'] = summary;
    if (tags != null) map['tags'] = tags;
    if (isPublished != null) map['is_published'] = isPublished;
    return map;
  }
}

class PostListResponse {
  final List<Post> items;
  final int total;

  PostListResponse({required this.items, required this.total});

  factory PostListResponse.fromJson(Map<String, dynamic> json) {
    return PostListResponse(
      items:
          (json['posts'] as List? ?? []).map((e) => Post.fromJson(e)).toList(),
      total: json['total'] ?? 0,
    );
  }
}
