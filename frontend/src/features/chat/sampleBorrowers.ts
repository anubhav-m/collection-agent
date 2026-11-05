// Fictional borrowers from backend/app/db/seed_data. Dates of birth are all 1 January and
// ZIP codes use the unassigned 000xx range, so none can match a real person.

export interface SampleBorrower {
  id: string
  name: string
  lenderId: string
  lenderName: string
  dateOfBirth: string
  zip: string
  situation: string
  starters: string[]
}

const verify = (b: Pick<SampleBorrower, 'name' | 'dateOfBirth' | 'zip'>) =>
  `Hi, I'm ${b.name}, date of birth ${b.dateOfBirth}, ZIP ${b.zip}.`

const JORDAN = { name: 'Jordan Samplebury', dateOfBirth: '1975-01-01', zip: '00002' }
const CASEY = { name: 'Casey Placeholder', dateOfBirth: '1968-01-01', zip: '00004' }
const HARPER = { name: 'Harper Notreal', dateOfBirth: '1988-01-01', zip: '00008' }
const ROWAN = { name: 'Rowan Fictionale', dateOfBirth: '1972-01-01', zip: '00009' }

export const SAMPLE_BORROWERS: SampleBorrower[] = [
  {
    id: 'BRW-002',
    ...JORDAN,
    lenderId: 'LND-001',
    lenderName: 'Maple Grove Example Credit',
    situation: 'Personal loan, $120.00 past due, 12 days late.',
    starters: [
      `${verify(JORDAN)} I'd like to set up a payment plan.`,
      'Can I pay it in 3 monthly payments starting next week?',
      'What happens if I miss a payment?',
    ],
  },
  {
    id: 'BRW-004',
    ...CASEY,
    lenderId: 'LND-001',
    lenderName: 'Maple Grove Example Credit',
    situation: 'Credit card, $300.00 past due, 45 days late.',
    starters: [
      `${verify(CASEY)} What do I owe right now?`,
      "I lost my job last month and I can't afford anything right now.",
    ],
  },
  {
    id: 'BRW-008',
    ...HARPER,
    lenderId: 'LND-002',
    lenderName: 'Riverbend Sample Finance',
    situation:
      'Personal loan, $250.00 past due, 30 days late. The second starter gives a wrong ZIP.',
    starters: [
      'Do you offer a settlement discount if I pay today?',
      `Hi, I'm ${HARPER.name}, date of birth ${HARPER.dateOfBirth}, ZIP 00099.`,
    ],
  },
  {
    id: 'BRW-009',
    ...ROWAN,
    lenderId: 'LND-002',
    lenderName: 'Riverbend Sample Finance',
    situation: 'Credit card, $1,200.00 past due, 58 days late.',
    starters: [`${verify(ROWAN)} I already paid this off in full last month.`],
  },
]
