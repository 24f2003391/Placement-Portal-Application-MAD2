<script setup>
import { RouterLink ,RouterView,useRouter} from 'vue-router';
import { useMessageStore } from './stores/message';
import { useAuthStore } from './stores/auth';
import { computed } from 'vue';

const router=useRouter()

const auth_store = useAuthStore();
const message_store = useMessageStore();

const messages = computed(() => {
  return message_store.messages;
});
async function logout() {
  try {
    const res = await fetch('http://127.0.0.1:5000/api/logout', {
      method: 'POST',
      headers: {
        'Authorization': auth_store.getAuthToken(),
        'Content-Type': 'application/json',
      }
    });
    if (!res.ok) {
      throw new Error(`Logout failed: ${res.status}`);
    }
    const data = await res.json();
    auth_store.clearAuthToken();
    message_store.updateMessages(data.message);
    router.push({name:'home'})
  } catch (err) {
    console.error('Logout failed', err);
  }
}

const isAdmin = computed(() => {
  return auth_store.isAuthenticated.value && user.value?.roles?.includes("admin")
})

const isStudent = computed(() => {
  return auth_store.isAuthenticated.value && user.value?.roles?.includes("student")
})

const isCompany = computed(() => {
  return auth_store.isAuthenticated.value && user.value?.roles?.includes("company")
})

const placeMateLink = computed(() => {
  const roles = getUserRoles()
  if (!roles || roles.length === 0) return '/'
  if (roles[0] === 'admin') return '/admin'
  if (roles[0] === 'company') return '/company'
  if (roles[0] === 'student') return '/student'
  return '/'
})
</script>

<template>
  <div class="bg-light min-vh-100">
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <RouterLink class="navbar-brand" :to=placeMateLink>PlaceMate</RouterLink>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" 
                data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" 
                aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <template v-if="isAdmin">
              <li class="nav-item"><RouterLink class="nav-link" to="/admin/companies">Companies</RouterLink></li>
              <li class="nav-item"><RouterLink class="nav-link" to="/admin/students">Students</RouterLink></li>
              <li class="nav-item"><RouterLink class="nav-link" to="/admin/placement-drives">Placement Drives</RouterLink></li>
              <li class="nav-item"><RouterLink class="nav-link" to="/admin/programs">Programs</RouterLink></li>
              <li class="nav-item"><a class="nav-link" href="#" @click.prevent="logout">Logout</a></li>
            </template>

            <template v-else-if="isCompany">
              <li class="nav-item"><RouterLink class="nav-link" to="/company/placement-drives">Placement Drives</RouterLink></li>
              <li class="nav-item"><a class="nav-link" href="#" @click.prevent="logout">Logout</a></li>
            </template>

            <template v-else-if="isStudent">
              <li class="nav-item"><RouterLink class="nav-link" to="/student/placement-drives">Placement Drives</RouterLink></li>
              <li class="nav-item"><RouterLink class="nav-link" to="/student/edit-profile">Edit Profile</RouterLink></li>
              <li class="nav-item"><RouterLink class="nav-link" to="/student/history">History</RouterLink></li>
              <li class="nav-item"><a class="nav-link" href="#" @click.prevent="logout">Logout</a></li>
            </template>

            <template v-else>
              <li class="nav-item"><RouterLink class="nav-link" to="/register-company">Register Company</RouterLink></li>
              <li class="nav-item"><RouterLink class="nav-link" to="/register-student">Register Student</RouterLink></li>
              <li class="nav-item"><RouterLink class="nav-link" to="/login">Login</RouterLink></li>
            </template>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container-fluid">
      <p class="text-center mt-3" v-if="messages">{{ messages }}</p>
      <RouterView></RouterView>
    </div>

  </div>
</template>