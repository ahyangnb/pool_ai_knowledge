import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import '../l10n/app_strings.dart';
import '../providers/locale_provider.dart';
import '../providers/post_detail_provider.dart';
import '../widgets/empty_state.dart';
import '../widgets/loading_indicator.dart';

class PostDetailPage extends ConsumerWidget {
  final String postId;
  const PostDetailPage({super.key, required this.postId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(localeProvider);
    final s = AppStrings.of(locale);
    final postAsync = ref.watch(postDetailProvider(postId));
    final colorScheme = Theme.of(context).colorScheme;

    return postAsync.when(
      loading: () => const LoadingIndicator(),
      error: (_, _) => EmptyState(message: s.detailNotFound),
      data: (post) {
        final dateStr = post.createdAt != null
            ? DateFormat('yyyy-MM-dd').format(post.createdAt!)
            : '';

        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Back button
              TextButton.icon(
                onPressed: () {
                  if (context.canPop()) {
                    context.pop();
                  } else {
                    context.go('/posts');
                  }
                },
                icon: const Icon(Icons.arrow_back, size: 18),
                label: Text(s.detailBack),
              ),

              const SizedBox(height: 16),

              // Title
              Text(
                post.title,
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      height: 1.4,
                    ),
              ),

              const SizedBox(height: 16),

              // Tags + date
              Wrap(
                spacing: 8,
                runSpacing: 8,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  ...post.tags.map((tag) => Chip(
                        label: Text(tag),
                        visualDensity: VisualDensity.compact,
                      )),
                  if (dateStr.isNotEmpty)
                    Text(
                      dateStr,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                    ),
                ],
              ),

              const Divider(height: 32),

              // Markdown content
              MarkdownBody(
                data: post.content,
                selectable: true,
                styleSheet: MarkdownStyleSheet(
                  h1: Theme.of(context).textTheme.headlineMedium,
                  h2: Theme.of(context).textTheme.headlineSmall,
                  h3: Theme.of(context).textTheme.titleLarge,
                  p: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        height: 1.8,
                      ),
                  code: TextStyle(
                    fontSize: 14,
                    backgroundColor: colorScheme.surfaceContainerLow,
                  ),
                  codeblockDecoration: BoxDecoration(
                    color: colorScheme.surfaceContainerLow,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  blockquoteDecoration: BoxDecoration(
                    border: Border(
                      left: BorderSide(color: colorScheme.primary, width: 4),
                    ),
                  ),
                  blockquotePadding: const EdgeInsets.only(left: 16),
                ),
                onTapLink: (_, href, _) {
                  if (href != null) launchUrl(Uri.parse(href));
                },
              ),

              const Divider(height: 48),

              // CTA section
              Center(
                child: Column(
                  children: [
                    Text(
                      s.detailChatCta,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                    ),
                    const SizedBox(height: 12),
                    FilledButton.icon(
                      onPressed: () {
                        final title = Uri.encodeComponent(post.title);
                        context.go(
                            '/chat?postId=${post.id}&postTitle=$title');
                      },
                      icon: const Icon(Icons.chat_outlined),
                      label: Text(s.detailAskAi),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 32),
            ],
          ),
        );
      },
    );
  }
}
