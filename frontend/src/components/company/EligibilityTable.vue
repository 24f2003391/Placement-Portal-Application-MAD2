<script setup>
defineProps({
  eligibility: {
    type: Array,
    required: true
  }
})
</script>

<template>

<div class="card mb-4">

    <div class="card-header">
        <h5 class="mb-0">
            Eligibility Criteria
        </h5>
    </div>

    <div class="card-body p-0">

        <table class="table table-bordered table-hover mb-0">

            <thead class="table-light">

                <tr>
                    <th>Program</th>
                    <th>Minimum CGPA</th>
                    <th>Eligible Year</th>
                </tr>

            </thead>

            <tbody>

                <tr
                    v-for="e in eligibility"
                    :key="e.eligibility_id">

                    <td>
                        {{ e.program_name }}
                    </td>

                    <td>
                        {{ e.min_cgpa }}
                    </td>

                    <td>
                        {{ e.eligible_year }}
                    </td>

                </tr>

                <tr v-if="eligibility.length === 0">

                    <td
                        colspan="3"
                        class="text-center text-muted">

                        No eligibility criteria added.

                    </td>

                </tr>

            </tbody>

        </table>

    </div>

</div>

</template>