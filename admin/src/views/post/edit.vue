<template>
  <post-form :is-edit="true" />
</template>

<script>
import PostForm from './components/PostForm'

export default {
  name: 'EditPost',
  components: { PostForm }
}
</script>
