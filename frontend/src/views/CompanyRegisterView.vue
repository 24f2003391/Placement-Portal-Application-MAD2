<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMessageStore } from '@/stores/message';

const router=useRouter();
const messageStore = useMessageStore()

const email = ref('');
const password = ref('');
const name = ref('');
const industry = ref('');
const hr_phone = ref('');
const website = ref('');

const passerror = ref('');
const emailStatus = ref('');
const phoneStatus = ref('');
const formError = ref('');

const validatePassword = () => {
  if (password.value.length < 8) {
    passerror.value = 'Password must be at least 8 characters long'
    return false
  } else {
    passerror.value = ''
    return true
  }
}

const checkEmail = async () => {
  emailStatus.value = ''
  if (!email.value) return
  try {
    const response = await fetch('http://127.0.0.1:5000/api/check-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value })
    })
    const data = await response.json()
    if (!response.ok) {
      messageStore.updateMessages(`Email check failed: ${data.message}`, 'danger')
      return
    } else {
      emailStatus.value = data.available
        ? '✅ Email available'
        : '❌ Email already registered'
    }
  } catch (error) {
    alert('Something went wrong while checking email')
    console.error(error)
  }
}

const checkPhone = async () => {
  phoneStatus.value = ''
  if (!hr_phone.value) return

  try {
    const response = await fetch('http://127.0.0.1:5000/api/check-phone', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone_no: hr_phone.value })
    })

    const data = await response.json()
    if (!response.ok) {
      messageStore.updateMessages(`Phone check failed: ${data.message}`, 'danger')
      return
    } else {
      phoneStatus.value = data.available
        ? '✅ Phone available'
        : '❌ Phone already registered'
    }
  } catch (error) {
    alert('Something went wrong while checking phone number')
    console.error(error)
  }
}

async function register() {
  formError.value = ''
  if (!validatePassword()) {
    messageStore.updateMessages('Invalid password length', 'danger')
    return
  }

  if (!email.value || !password.value || !name.value || !industry.value || !hr_phone.value) {
    messageStore.updateMessages('Please fill all required fields', 'danger')
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/company/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        name: name.value,
        industry: industry.value,
        hr_phone: hr_phone.value,
        website: website.value
      })
    })

    const data = await response.json()
    if (!response.ok) {
      formError.value = data.message
      return
    }
    messageStore.updateMessages(data.message)
    router.push({name:'login'})
  } catch (error) {
    formError.value = 'Something went wrong'
    console.error(error)
  }
}
</script>

<template>
  <div class="container-fluid d-flex justify-content-center align-items-center  pt-5 bg-light">
    <div class="card shadow p-4" style="width: 400px;">
      <h3 class="text-center mb-4">Company Register</h3>

      <form @submit.prevent="register">

        <div class="mb-3">
          <label for="name" class="form-label">Company Name</label>
          <input 
            id="name"
            type="text"
            class="form-control" 
            v-model="name" 
            placeholder="Enter company name"
          >
        </div>

        <div class="mb-3">
          <label for="industry" class="form-label">Industry</label>
          <input 
            id="industry"
            type="text"
            class="form-control" 
            v-model="industry" 
            placeholder="Enter industry"
          >
        </div>

        <div class="mb-3">
          <label for="phone" class="form-label">HR Phone</label>
          <input 
            id="phone"
            type="text"
            class="form-control" 
            v-model="hr_phone" 
            placeholder="Enter HR phone number"
            @blur="checkPhone"
          >
          <div class="form-text">{{ phoneStatus }}</div>
        </div>

        <div class="mb-3">
          <label for="email" class="form-label">Email Address</label>
          <input 
            id="email"
            type="email"
            class="form-control" 
            v-model="email" 
            placeholder="Enter email"
            @blur="checkEmail"
          >
          <div class="form-text">{{ emailStatus }}</div>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input 
            id="password"
            type="password"
            class="form-control"
            v-model="password"
            @input="validatePassword"
            placeholder="Enter password"
          >
          <div class="form-text text-danger">{{ passerror }}</div>
        </div>

        <div class="mb-3">
          <label for="website" class="form-label">Website (optional)</label>
          <input 
            id="website"
            type="text"
            class="form-control" 
            v-model="website" 
            placeholder="Enter website URL"
          >
        </div>

        <div class="text-danger mb-2">{{ formError }}</div>

        <button class="btn btn-success w-100">Register</button>

      </form>
    </div>
  </div>
</template>