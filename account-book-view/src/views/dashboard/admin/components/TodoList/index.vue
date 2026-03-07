<template>
  <section class="todoapp">
    <!-- header -->
    <header class="header">
      <input
        :maxlength="45"
        class="new-todo"
        autocomplete="off"
        placeholder="財務目標"
        @keyup.enter="addTodo"
      >
    </header>
    <!-- main section -->
    <section v-show="todos.length" class="main">
      <!-- <input
        id="toggle-all"
        :checked="allChecked"
        class="toggle-all"
        type="checkbox"
        @change="toggleAll({ is_done: !allChecked })"
      />
      <label for="toggle-all" /> -->
      <ul class="todo-list">
        <todo
          v-for="(todo, index) in filteredTodos"
          :key="index"
          :todo="todo"
          @toggleTodo="toggleTodo"
          @editTodo="editTodo"
          @deleteTodo="deleteTodo"
        />
      </ul>
    </section>
    <!-- footer -->
    <footer v-show="todos.length" class="footer">
      <span class="todo-count">
        <strong>{{ remaining }}</strong>
        {{ remaining | pluralize('item') }} left
      </span>
      <ul class="filters">
        <li v-for="(val, key) in filters" :key="key">
          <a
            :class="{ selected: visibility === key }"
            @click.prevent="visibility = key"
          >{{ key | capitalize }}</a
          >
        </li>
      </ul>
      <!-- <button class="clear-completed" v-show="todos.length > remaining" @click="clearCompleted">
        Clear completed
      </button> -->
    </footer>
  </section>
</template>

<script>
import Todo from './Todo.vue'

const filters = {
  all: (todos) => todos,
  active: (todos) => todos.filter((todo) => todo.is_done === 'N'),
  completed: (todos) => todos.filter((todo) => todo.is_done === 'Y')
}

export default {
  components: { Todo },
  filters: {
    pluralize: (n, w) => (n === 1 ? w : w + 's'),
    capitalize: (s) => s.charAt(0).toUpperCase() + s.slice(1)
  },
  data() {
    return {
      visibility: 'all',
      filters,
      todos: []
    }
  },
  computed: {
    // allChecked() {
    //   return this.todos.every((todo) => todo.is_done)
    // },
    filteredTodos() {
      return filters[this.visibility](this.todos)
    },
    remaining() {
      return this.todos.filter((todo) => !todo.is_done).length
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.$store.dispatch('GetTargetList').then((response) => {
        this.todos = response.data
      })
    },
    addTodo(e) {
      const text = e.target.value
      if (text.trim()) {
        this.$store.dispatch('AddTarget', { setting_value: text }).then(() => {
          this.fetchData()
        })
      }

      e.target.value = ''
    },
    toggleTodo(data) {
      data.is_done = data.is_done === 'Y' ? 'N' : 'Y'
      this.$store.dispatch('UpdateTarget', data)
    },
    deleteTodo(todo) {
      this.todos.splice(this.todos.indexOf(todo), 1)
      this.$store.dispatch('DeleteTarget', todo.distinct_number)
    },
    editTodo({ todo, value }) {
      todo.setting_value = value
    }
    // clearCompleted() {
    //   this.todos = this.todos.filter((todo) => !todo.is_done)
    //   this.setLocalStorage()
    // }
    // toggleAll({ is_done }) {
    //   this.todos.forEach((todo) => {
    //     todo.is_done = is_done
    //     this.setLocalStorage()
    //   })
    // }
  }
}
</script>

<style lang="scss">
@import './index.scss';
</style>
