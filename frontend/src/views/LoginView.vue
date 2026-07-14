<script setup>
import {ref} from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useMessageStore } from '@/stores/message'
import { useRouter } from 'vue-router'

const router = useRouter()

const messageStore = useMessageStore()

const auth_store=useAuthStore()
const email =ref('');
const password=ref('');

const passerror=ref('');

const validatePassword=()=>{
    if (password.value.length<8){
        passerror.value='The password must be atleast 8 characters long'
        return false
    }else{
        passerror.value=''
        return true
    } 
}

async function login(){
    if (!validatePassword() ){
        messageStore.updateMessages(
    'Password must be at least 8 characters long',
    'danger'
)
        return}

    if (email.value === ''|| password.value === '') {
        messageStore.updateMessages(
    'Please fill in all the fields',
    'danger'
)
        return}

        try {
        const response= await fetch("http://127.0.0.1:5000/api/login",{
            method:"POST",
            headers:{
                "Content-Type": 'application/json'
            },
            body:JSON.stringify({"email":email.value,
                "password":password.value})
        })
        if(!response.ok){
            const errorData = await response.json();
            messageStore.updateMessages(
    `Login failed: ${errorData.message}`,
    'danger'
)
            return;
        }
        else{
            const data= await response.json();
            const user = {
                id: data.data.user.id,
                roles: data.data.user.roles,}
            auth_store.setUserCred(data.data.auth_token, user)
            messageStore.updateMessages(data.message)
            if (user.roles.includes('admin'))
                router.push('/admin')

            else if (user.roles.includes('student'))
                router.push('/student')

            else if (user.roles.includes('company'))
                router.push('/company')
            return;
        }}
        catch (error){
            alert('Something went wrong')
            console.error(error)
        }
    }
</script>

<template>
    <div class="container-fluid d-flex justify-content-center align-items-center  pt-5 bg-light">
        <div class="card shadow p-4" style="width: 350px; border-radius: 12px;">
            <h3 class="text-center mb-4">Login</h3>
            
            <form v-on:submit.prevent="login">
                <div class="mb-3">
                    <label for="email" class="form-label">Email address</label>
                    <input
                        type="email" id="email" name="email" class="form-control" placeholder="Enter email" 
                        v-model="email">
                    </div>

                    <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input
                        type="password" id="password" name="password"
                        class="form-control" placeholder="Enter password" v-model="password" v-on:input="validatePassword" aria-describedby="passwordHelp">
                    <div id="passwordHelp" class="form-text">{{ passerror }}</div>
                </div>

                <button type="submit" class="btn btn-primary w-100">Submit</button>
            </form>
        </div>
    </div>
</template>