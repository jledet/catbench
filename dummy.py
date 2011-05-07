# Dummy data for testing catplot
dummy = {
    'coding': {
        'slaves': {
            'alice': {
                100: [{'throughput': 100, 'jitter': 23.3, 'lost': 1, 'total': 100, 'pl': 1.1},
                      {'throughput': 98,  'jitter': 22.9, 'lost': 1, 'total': 100, 'pl': 1.2}], 
                200: [{'throughput': 199, 'jitter': 27.9, 'lost': 1, 'total': 200, 'pl': 1.1}, 
                      {'throughput': 196, 'jitter': 27.9, 'lost': 1, 'total': 200, 'pl': 1.1}]
                }, 
            'bob':   {
                100: [{'throughput': 99,  'jitter': 23.3, 'lost': 1, 'total': 100, 'pl': 1.1}, 
                      {'throughput': 94,  'jitter': 22.9, 'lost': 1, 'total': 100, 'pl': 1.2}],
                200: [{'throughput': 197, 'jitter': 27.9, 'lost': 1, 'total': 200, 'pl': 1.1},
                      {'throughput': 196, 'jitter': 27.9, 'lost': 1, 'total': 200, 'pl': 1.1}],
                },
            },
        'nodes': {
            'alice': {
                100: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]],
                200: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]]
                },
            'bob': {
                100: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]],
                200: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]]
                },
            'relay': {
                100: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]],
                200: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]]
                },    
            },
        },
    'nocoding': {
        'slaves': {
            'alice': {
                100: [{'throughput': 99,  'jitter': 23.3, 'lost': 1, 'total': 100, 'pl': 1.1},
                      {'throughput': 96,  'jitter': 22.9, 'lost': 1, 'total': 100, 'pl': 1.2}], 
                200: [{'throughput': 194, 'jitter': 27.9, 'lost': 1, 'total': 200, 'pl': 1.1},
                      {'throughput': 200, 'jitter': 27.9, 'lost': 1, 'total': 200, 'pl': 1.1}]
                }, 
            'bob':   {
                100: [{'throughput': 99,  'jitter': 23.3, 'lost': 1, 'total': 100, 'pl': 1.1},
                      {'throughput': 95,  'jitter': 22.9, 'lost': 1, 'total': 100, 'pl': 1.2}],
                200: [{'throughput': 197, 'jitter': 27.9, 'lost': 1, 'total': 200, 'pl': 1.1},
                      {'throughput': 199, 'jitter': 27.9, 'lost': 1, 'total': 200, 'pl': 1.1}],
                },
            },
        'nodes': {
            'alice': {
                100: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]],
                200: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]]
                },
            'bob': {
                100: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]],
                200: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]]
                },
            'relay': {
                100: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]],
                200: [[{"coded": 100, "forwarded": 50}, {"coded": 200, "forwarded": 100}, {"coded": 300, "forwarded": 150}],
                      [{"coded": 200, "forwarded": 100}, {"coded": 400, "forwarded": 200}, {"coded": 600, "forwarded": 300}]]
                },    
            },
        },
}

