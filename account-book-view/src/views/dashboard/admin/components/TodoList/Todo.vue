<template>
  <li
    :class="{ completed: todo.is_done === 'Y', editing: editing }"
    class="todo"
  >
    <div :class="{ checked: todo.is_done === 'Y' }" class="view">
      <input
        :checked="todo.is_done === 'Y'"
        class="toggle"
        type="checkbox"
        @change="toggleTodo(todo)"
      >
      <label v-text="todo.target_year" />
      <label @dblclick="editing = true" v-text="todo.setting_value" />
      <button class="destroy" @click="deleteTodo(todo)" />
    </div>
    <input
      v-focus="editing"
      v-show="editing"
      :value="todo.setting_value"
      class="edit"
      @keyup.enter="doneEdit"
      @keyup.esc="cancelEdit"
      @blur="cancelEdit"
    >
  </li>
</template>

<script>
export default {
  name: 'Todo',
  directives: {
    focus(el, { value }, { context }) {
      if (value) {
        context.$nextTick(() => {
          el.focus()
        })
      }
    }
  },
  props: {
    todo: {
      type: Object,
      default: function() {
        return {}
      }
    }
  },
  data() {
    return {
      editing: false
    }
  },
  methods: {
    deleteTodo(todo) {
      this.$emit('deleteTodo', todo)
    },
    // editTodo({ todo, value }) {
    //   this.$emit('editTodo', { todo, value })
    // },
    toggleTodo(todo) {
      this.$emit('toggleTodo', todo)
    },
    doneEdit(e) {
      const value = e.target.value.trim()
      if (!value) {
        this.deleteTodo(this.todo)
      } else if (this.editing) {
        const data = JSON.parse(JSON.stringify(this.todo))
        data.setting_value = value
        this.$store.dispatch('UpdateTarget', data).then(() => {
          this.editing = false
          this.$emit('editTodo', { todo: this.todo, value })
        })
      }
    },
    cancelEdit(e) {
      e.target.value = this.todo.setting_value
      this.editing = false
    }
  }
}
</script>
