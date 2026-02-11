<template>
  <post-form :is-edit="false" />
</template>

<script>
import PostForm from './components/PostForm'

export default {
  name: 'CreatePost',
  components: { PostForm }
}
</script>
