<script setup>
const props = defineProps({
  interviews: {
    type: Array,
    required: true
  }
})

const emit = defineEmits([
  'cancel',
  'complete'
])

function badgeClass(status) {
  switch (status) {
    case 'Scheduled':
      return 'bg-primary'

    case 'Completed':
      return 'bg-success'

    case 'Cancelled':
      return 'bg-danger'

    default:
      return 'bg-secondary'
  }
}
</script>

<template>

<div class="card mb-4">

    <div class="card-header">
        <h5 class="mb-0">
            Scheduled Interviews
        </h5>
    </div>

    <div class="card-body p-0">

        <table class="table table-bordered table-hover mb-0">

            <thead class="table-light">

                <tr>

                    <th>Roll No</th>

                    <th>Student</th>

                    <th>Date & Time</th>

                    <th>Interview Details</th>

                    <th>Status</th>

                    <th>Actions</th>

                </tr>

            </thead>

            <tbody>

                <tr
                    v-for="interview in interviews"
                    :key="interview.id">

                    <td>

                        {{ interview.roll_no }}

                    </td>

                    <td>

                        {{ interview.student_name }}

                    </td>

                    <td>

                        {{ interview.interview_datetime }}

                    </td>

                    <td>

                        {{ interview.interview_details }}

                    </td>

                    <td>

                        <span
                            class="badge"
                            :class="badgeClass(interview.status)">

                            {{ interview.status }}

                        </span>

                    </td>

                    <td>

                        <button
                            v-if="interview.status=='Scheduled'"
                            class="btn btn-success btn-sm me-2"
                            @click="emit('complete', interview.id)">

                            Mark Completed

                        </button>

                        <button
                            v-if="interview.status=='Scheduled'"
                            class="btn btn-danger btn-sm"
                            @click="emit('cancel', interview.id)">

                            Cancel

                        </button>

                        <span
                            v-if="interview.status!='Scheduled'"
                            class="text-muted">

                            —

                        </span>

                    </td>

                </tr>

                <tr
                    v-if="interviews.length===0">

                    <td
                        colspan="6"
                        class="text-center text-muted">

                        No interviews scheduled.

                    </td>

                </tr>

            </tbody>

        </table>

    </div>

</div>

</template>